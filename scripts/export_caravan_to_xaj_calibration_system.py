"""
Export CARAVAN (netcdf) basin time series to the input format required by an
external "XAJ Calibration System":

- DataInput.xlsx
  - Sheet name: ABC
  - Columns (case-sensitive): 时间, P, E, Q
    - 时间: datetime (e.g., 2005-01-01)
    - P: precipitation (mm)
    - E: evaporation / PET (mm)
    - Q: observed discharge (m3/s)

- Floodevents.csv
  - Columns: ID,start,end
  - start/end are 0-based slice indices aligned to the Excel data rows:
    - Excel data row index (first data row is row 2): i = 0..N-1
    - start = i_start
    - end = i_end + 1  (end-exclusive)

This script reads directly from CARAVAN per-basin NetCDF files to avoid building
large hydrodataset caches.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


REGION_CODE_TO_FOLDER = {
    "US": "camels",
    "AUS": "camelsaus",
    "BR": "camelsbr",
    "CL": "camelscl",
    "GB": "camelsgb",
    "NA": "hysets",
    "CE": "lamah",
}


@dataclass(frozen=True)
class Event:
    start_idx: int  # inclusive, 0-based relative to first data row
    end_idx_excl: int  # exclusive


def _resolve_region_folder(region: str) -> str:
    region = str(region).strip()
    return REGION_CODE_TO_FOLDER.get(region, region)


def _pick_pet_var(ds: xr.Dataset, pet_preference: str) -> str:
    pref = str(pet_preference).strip().upper()
    candidates: list[str] = []
    if pref in {"FAO", "FAO_PM", "FAO_PENMAN_MONTEITH"}:
        candidates.append("potential_evaporation_sum_FAO_PENMAN_MONTEITH")
    if pref in {"ERA5", "ERA5_LAND"}:
        candidates.append("potential_evaporation_sum_ERA5_LAND")
    candidates.extend(
        [
            "potential_evaporation_sum_FAO_PENMAN_MONTEITH",
            "potential_evaporation_sum_ERA5_LAND",
        ]
    )
    for v in candidates:
        if v in ds.data_vars:
            return v
    raise KeyError(f"PET variable not found. Tried: {candidates}")


def _load_area_km2(caravan_dir: Path, region_folder: str, basin_id: str) -> float:
    # Most subsets expose area + gauge coords here
    attr_other = (
        caravan_dir
        / "attributes"
        / region_folder
        / f"attributes_other_{region_folder}.csv"
    )
    if not attr_other.exists():
        raise FileNotFoundError(f"Attributes file not found: {attr_other}")
    df = pd.read_csv(attr_other)
    row = df[df["gauge_id"].astype(str) == str(basin_id)]
    if row.empty:
        raise ValueError(f"gauge_id not found in {attr_other}: {basin_id}")
    return float(row.iloc[0]["area"])


def _mmday_to_m3s(q_mmday: np.ndarray, area_km2: float) -> np.ndarray:
    # mm/day over basin area -> m3/s
    # Q(m3/s) = Q(mm/day) * area(km2) * 1e6(m2/km2) * 0.001(m/mm) / 86400(s/day)
    factor = area_km2 * 1000.0 / 86400.0
    return q_mmday * factor


def _detect_events(
    p_mm: np.ndarray,
    q_cms: np.ndarray,
    p_threshold: float,
    q_threshold: float,
    pre_buffer_days: int,
    post_buffer_days: int,
    min_event_days: int,
) -> list[Event]:
    p = np.asarray(p_mm, dtype=float)
    q = np.asarray(q_cms, dtype=float)
    trigger = (p >= float(p_threshold)) | (q >= float(q_threshold))
    trigger = np.where(np.isfinite(trigger), trigger, False)

    idx = np.where(trigger)[0]
    if idx.size == 0:
        return []

    events: list[Event] = []
    # group contiguous indices
    start = int(idx[0])
    prev = int(idx[0])
    for cur in idx[1:]:
        cur = int(cur)
        if cur == prev + 1:
            prev = cur
            continue
        # close segment
        seg_start = max(0, start - pre_buffer_days)
        seg_end_excl = min(len(p), prev + 1 + post_buffer_days)
        if (seg_end_excl - seg_start) >= int(min_event_days):
            events.append(Event(seg_start, seg_end_excl))
        start = cur
        prev = cur

    # last segment
    seg_start = max(0, start - pre_buffer_days)
    seg_end_excl = min(len(p), prev + 1 + post_buffer_days)
    if (seg_end_excl - seg_start) >= int(min_event_days):
        events.append(Event(seg_start, seg_end_excl))

    # merge overlaps
    if not events:
        return []
    events_sorted = sorted(events, key=lambda e: e.start_idx)
    merged: list[Event] = [events_sorted[0]]
    for e in events_sorted[1:]:
        last = merged[-1]
        if e.start_idx <= last.end_idx_excl:
            merged[-1] = Event(last.start_idx, max(last.end_idx_excl, e.end_idx_excl))
        else:
            merged.append(e)
    return merged


def parse_args():
    p = argparse.ArgumentParser(
        description="Export CARAVAN basin data to XAJ Calibration System inputs."
    )
    p.add_argument(
        "--caravan-dir",
        required=True,
        help="Path to the CARAVAN dataset folder that contains attributes/, timeseries/, shapefiles/ (e.g., Caravan-Jan25-nc).",
    )
    p.add_argument(
        "--region",
        default="US",
        help="Region code (US/AUS/BR/CL/GB/NA/CE) or region folder name (camels/camelsaus/...).",
    )
    p.add_argument(
        "--basin-id",
        required=True,
        help="Basin/gauge id (e.g., camels_01013500).",
    )
    p.add_argument(
        "--start",
        required=True,
        help="Start date (YYYY-MM-DD).",
    )
    p.add_argument(
        "--end",
        required=True,
        help="End date (YYYY-MM-DD).",
    )
    p.add_argument(
        "--pet-preference",
        default="FAO_PENMAN_MONTEITH",
        help="PET variable to use: FAO_PENMAN_MONTEITH or ERA5_LAND.",
    )
    p.add_argument(
        "--out-dir",
        default="data",
        help="Output folder (will contain DataInput.xlsx and Floodevents.csv). Default: ./data",
    )
    p.add_argument(
        "--time-scale-hours",
        type=float,
        default=None,
        help="Time scale (hours) to show in the external calibration UI. Default: auto (24 for daily data).",
    )
    p.add_argument(
        "--iterations",
        type=int,
        default=5000,
        help="Suggested iteration count for the external SCE-UA UI. Default: 5000.",
    )
    p.add_argument(
        "--re-threshold",
        type=float,
        default=0.10,
        help="Suggested RE (relative error) threshold for the external UI. Default: 0.10 (10%).",
    )

    # event detection
    p.add_argument("--p-threshold", type=float, default=1.0, help="P threshold (mm/day) to trigger an event.")
    p.add_argument("--q-threshold", type=float, default=1.0, help="Q threshold (m3/s) to trigger an event.")
    p.add_argument("--pre-buffer-days", type=int, default=1, help="Days to include before trigger.")
    p.add_argument("--post-buffer-days", type=int, default=3, help="Days to include after trigger.")
    p.add_argument("--min-event-days", type=int, default=3, help="Minimum event window length in days.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    caravan_dir = Path(args.caravan_dir).resolve()
    region_folder = _resolve_region_folder(args.region)
    basin_id = str(args.basin_id)

    ts_nc = (
        caravan_dir
        / "timeseries"
        / "netcdf"
        / region_folder
        / f"{basin_id}.nc"
    )
    if not ts_nc.exists():
        raise FileNotFoundError(f"Timeseries NetCDF not found: {ts_nc}")

    area_km2 = _load_area_km2(caravan_dir, region_folder, basin_id)

    with xr.open_dataset(ts_nc) as ds0:
        time_dim = "date" if "date" in ds0.coords or "date" in ds0.dims else "time"
        if time_dim not in ds0:
            raise KeyError(f"Could not find time coordinate 'date' or 'time' in {ts_nc}")

        pet_var = _pick_pet_var(ds0, args.pet_preference)
        required = ["total_precipitation_sum", pet_var, "streamflow"]
        missing = [v for v in required if v not in ds0.data_vars]
        if missing:
            raise KeyError(f"Missing required vars in {ts_nc}: {missing}")

        ds = ds0[required].sel({time_dim: slice(args.start, args.end)}).load()
        if time_dim != "time":
            ds = ds.rename({time_dim: "time"})

    time = pd.to_datetime(ds["time"].values)
    p_mm = ds["total_precipitation_sum"].to_numpy().astype(float)
    e_mm = ds[pet_var].to_numpy().astype(float)
    q_mmday = ds["streamflow"].to_numpy().astype(float)
    q_cms = _mmday_to_m3s(q_mmday, area_km2)

    df = pd.DataFrame(
        {
            "时间": time,
            "P": p_mm,
            "E": e_mm,
            "Q": q_cms,
        }
    )

    # Suggest UI values
    time_scale_hours = args.time_scale_hours
    if time_scale_hours is None:
        # CARAVAN here is daily; if user exports other frequencies later, they can override.
        time_scale_hours = 24.0

    # Detect events on exported time range
    events = _detect_events(
        p_mm=p_mm,
        q_cms=q_cms,
        p_threshold=args.p_threshold,
        q_threshold=args.q_threshold,
        pre_buffer_days=args.pre_buffer_days,
        post_buffer_days=args.post_buffer_days,
        min_event_days=args.min_event_days,
    )

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write Excel
    xlsx_path = out_dir / "DataInput.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl", datetime_format="YYYY-MM-DD") as w:
        df.to_excel(w, sheet_name="ABC", index=False)

    # Write events CSV
    csv_path = out_dir / "Floodevents.csv"
    if events:
        df_events = pd.DataFrame(
            {
                "ID": list(range(1, len(events) + 1)),
                "start": [e.start_idx for e in events],
                "end": [e.end_idx_excl for e in events],
            }
        )
    else:
        df_events = pd.DataFrame({"ID": [], "start": [], "end": []})
    df_events.to_csv(csv_path, index=False, encoding="utf-8")

    # Write UI parameter note (for the external calibration system)
    params_path = out_dir / "CalibrationSystemParams.txt"
    params_text = "\n".join(
        [
            "XAJ Calibration System - Suggested UI inputs",
            "",
            f"- Basin ID: {basin_id}",
            f"- Data period: {args.start} .. {args.end}",
            "",
            "1) 流域面积(km2)",
            f"   {area_km2:.3f}",
            "",
            "2) 时间尺度(h)",
            f"   {float(time_scale_hours):.0f}",
            "   (本次导出为日尺度数据，所以应填 24；若你导出小时数据，再填 1)",
            "",
            "3) 迭代次数",
            f"   {int(args.iterations)}",
            "   (建议：先 2000-5000 快速试跑；正式可 10000-20000)",
            "",
            "4) RE误差阈值",
            f"   {float(args.re_threshold):.2f}",
            "",
            "数据文件说明：",
            f"- DataInput.xlsx: 列=时间,P(mm),E(mm),Q(m3/s)  Sheet=ABC",
            f"- Floodevents.csv: ID,start,end (0-based; end 为右开索引)",
            "",
            "注意：你软件里的“流域面积”用于模型内部换算/水量平衡，应尽量与本次 Q 换算一致。",
        ]
    )
    params_path.write_text(params_text, encoding="utf-8")

    print(f"[OK] Wrote: {xlsx_path}")
    print(f"[OK] Wrote: {csv_path} (events: {len(events)})")
    print(f"[OK] Wrote: {params_path}")
    print(f"[INFO] Basin: {basin_id}  Area(km2): {area_km2}")
    print(f"[INFO] PET var: {pet_var}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

