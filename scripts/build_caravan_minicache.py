"""
Build a minimal hydrodataset cache for a small set of CARAVAN basins.

Why:
- hydrodataset.Caravan will otherwise build huge cache batches for all basins in a region.
- hydromodel's training pipeline expects hydrodataset.read_ts_xrdataset(), which reads from cache.

This script creates:
- <cache_dir>/caravan_<region_folder>_timeseries_batch_<first>_<last>.nc
- <cache_dir>/caravan_attributes.nc  (minimal, containing at least `area` for the basins)

Assumptions:
- You have a CARAVAN dataset extracted and reachable via <data_root>/CARAVAN/
  (a junction/symlink to an existing folder also works).
- Timeseries per basin exists at:
    <data_root>/CARAVAN/timeseries/netcdf/<region_folder>/<basin_id>.nc
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


def _pick_temperature_var(ds: xr.Dataset) -> str | None:
    for v in (
        "temperature_2m_mean",
        "temperature_mean",
        "tmean",
        "tas",
        "temp",
    ):
        if v in ds.data_vars:
            return v
    return None


def _fallback_camels_nc_dir(repo_root: Path) -> Path | None:
    """Optional sibling hydrodata Caravan camels NetCDF (do not delete)."""
    candidates = [
        repo_root.parent / "hydrodata" / "Caravan" / "usr" / "local" / "google" / "home" / "kratzert" / "Data" / "Caravan-Jan25-nc" / "timeseries" / "netcdf" / "camels",
        repo_root.parent / "hydrodata" / "Caravan" / "timeseries" / "netcdf" / "camels",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _pick_pet_var(ds: xr.Dataset, preference: str) -> str:
    """
    CARAVAN netcdf may provide PET as multiple variants, e.g.:
    - potential_evaporation_sum_ERA5_LAND
    - potential_evaporation_sum_FAO_PENMAN_MONTEITH
    hydrodataset expects `potential_evaporation_sum`.
    """
    candidates = []
    pref = preference.strip().upper()
    if pref in {"FAO", "FAO_PM", "FAO_PENMAN_MONTEITH"}:
        candidates.append("potential_evaporation_sum_FAO_PENMAN_MONTEITH")
    if pref in {"ERA5", "ERA5_LAND"}:
        candidates.append("potential_evaporation_sum_ERA5_LAND")
    # fallback candidates
    candidates.extend(
        [
            "potential_evaporation_sum_FAO_PENMAN_MONTEITH",
            "potential_evaporation_sum_ERA5_LAND",
            "potential_evaporation_sum",
        ]
    )
    for v in candidates:
        if v in ds.data_vars:
            return v
    raise KeyError(
        "Could not find a PET variable. Looked for: "
        + ", ".join(dict.fromkeys(candidates))
    )


def _merge_area_attrs(existing: xr.Dataset, new: xr.Dataset) -> xr.Dataset:
    """Merge area-only attribute datasets on basin, de-duplicating basins."""
    if "area" not in existing.data_vars:
        return new
    if "area" not in new.data_vars:
        return existing

    ex_basins = [str(b) for b in existing["basin"].values.tolist()]
    new_basins = [str(b) for b in new["basin"].values.tolist()]

    ex_map = {b: float(existing["area"].sel(basin=b).values) for b in ex_basins}
    new_map = {b: float(new["area"].sel(basin=b).values) for b in new_basins}

    ex_map.update(new_map)  # new overwrites existing
    merged_basins = sorted(ex_map.keys())
    merged_area = np.array([ex_map[b] for b in merged_basins], dtype="float32")

    return xr.Dataset(
        data_vars={"area": (("basin",), merged_area, {"units": "km^2"})},
        coords={"basin": merged_basins},
    )


def _ensure_daily_time_index(ds: xr.Dataset, start: str, end: str) -> xr.Dataset:
    """Reindex to a continuous daily time axis to align multiple basins."""
    full_time = pd.date_range(start=start, end=end, freq="D")
    return ds.reindex(time=full_time)


def _batch_file_basins(nc_path: Path) -> set[str]:
    """Read basin ids stored in a timeseries batch cache file."""
    with xr.open_dataset(nc_path) as ds:
        return {str(b) for b in ds["basin"].values.tolist()}


def _remove_overlapping_batch_caches(
    cache_dir: Path, region_folder: str, basin_ids: list[str], keep_path: Path
) -> list[Path]:
    """Remove stale batch files that duplicate basins (hydrodataset concat_dim=basin)."""
    removed: list[Path] = []
    basin_set = set(basin_ids)
    pattern = f"caravan_{region_folder}_timeseries_batch_*.nc"
    for old in cache_dir.glob(pattern):
        if old.resolve() == keep_path.resolve():
            continue
        try:
            batch_basins = _batch_file_basins(old)
        except Exception:
            continue
        if basin_set & batch_basins:
            old.unlink()
            removed.append(old)
    return removed


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    os.chdir(repo_root)

    p = argparse.ArgumentParser(description="Build minimal CARAVAN cache for a few basins.")
    p.add_argument(
        "--data-root",
        required=True,
        help=(
            "Directory that contains the CARAVAN folder (i.e., <data-root>/CARAVAN). "
            "If your CARAVAN is nested like <data-root>/CARAVAN/Caravan/Caravan, this script "
            "will auto-detect the correct inner folder."
        ),
    )
    p.add_argument("--region-folder", default="camels", help="Region folder under timeseries/netcdf.")
    p.add_argument(
        "--basin-id",
        default=None,
        help="Single basin id / gauge id (e.g., camels_01013500).",
    )
    p.add_argument(
        "--basin-ids",
        nargs="+",
        default=None,
        help="Multiple basin ids. If provided, overrides --basin-id.",
    )
    p.add_argument(
        "--cache-dir",
        default=str(Path("_portable_data") / ".cache"),
        help="Cache output directory (default: ./_portable_data/.cache).",
    )
    p.add_argument(
        "--t-range",
        nargs=2,
        default=["1985-10-01", "2014-09-30"],
        help="Time range to store in cache: start end (YYYY-MM-DD).",
    )
    p.add_argument(
        "--pet-preference",
        default="FAO_PENMAN_MONTEITH",
        help="Which PET variant to use (FAO_PENMAN_MONTEITH or ERA5_LAND).",
    )
    args = p.parse_args()

    data_root = Path(args.data_root).resolve()

    # Accept multiple layouts:
    # 1) <data-root>/CARAVAN/<attributes,timeseries,shapefiles>
    # 2) <data-root>/CARAVAN/Caravan/Caravan/<attributes,timeseries,shapefiles> (as expected by hydrodataset)
    # 3) <data-root>/<attributes,timeseries,shapefiles> (direct folder)
    caravan_root = data_root / "CARAVAN"
    if caravan_root.exists():
        if (caravan_root / "Caravan" / "Caravan").exists():
            caravan_root = caravan_root / "Caravan" / "Caravan"
        elif (caravan_root / "attributes").exists():
            pass
        else:
            raise FileNotFoundError(
                f"Unrecognized CARAVAN layout under: {caravan_root}\n"
                "Expected either CARAVAN/attributes/... or CARAVAN/Caravan/Caravan/attributes/..."
            )
    else:
        # Direct folder layout (no CARAVAN wrapper)
        if (data_root / "attributes").exists() and (data_root / "timeseries").exists():
            caravan_root = data_root
        else:
            raise FileNotFoundError(
                f"CARAVAN not found under: {data_root}\n"
                "Expected <data-root>/CARAVAN/..., or pass a directory that directly contains attributes/ and timeseries/."
            )

    basin_ids = args.basin_ids if args.basin_ids else None
    if basin_ids is None:
        if not args.basin_id:
            raise ValueError("Must provide --basin-id or --basin-ids")
        basin_ids = [str(args.basin_id)]
    basin_ids = [str(b) for b in basin_ids]
    basin_ids = sorted(basin_ids)
    region_folder = str(args.region_folder)
    ts_dir = caravan_root / "timeseries" / "netcdf" / region_folder
    for bid in basin_ids:
        ts_file = ts_dir / f"{bid}.nc"
        if not ts_file.exists():
            raise FileNotFoundError(f"Timeseries netcdf not found: {ts_file}")

    cache_dir = Path(args.cache_dir).resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    start, end = args.t_range[0], args.t_range[1]

    required_common = ["total_precipitation_sum", "streamflow"]
    out_list = []
    pet_src_used = None
    temp_src_used = None
    for bid in basin_ids:
        ts_file = ts_dir / f"{bid}.nc"
        with xr.open_dataset(ts_file) as ds0:
            time_dim = "date" if "date" in ds0.coords or "date" in ds0.dims else "time"
            if time_dim not in ds0:
                raise KeyError(f"Could not find time coordinate 'date' or 'time' in {ts_file}")
            pet_src = _pick_pet_var(ds0, args.pet_preference)
            if pet_src_used is None:
                pet_src_used = pet_src

            temp_src = _pick_temperature_var(ds0)
            temp_from_fallback = None
            if temp_src is None:
                fallback_dir = _fallback_camels_nc_dir(repo_root)
                fallback_file = (
                    fallback_dir / f"{bid}.nc" if fallback_dir is not None else None
                )
                if fallback_file is not None and fallback_file.exists():
                    with xr.open_dataset(fallback_file) as ds_fb:
                        fb_temp = _pick_temperature_var(ds_fb)
                        if fb_temp is not None:
                            fb_time = "date" if "date" in ds_fb.coords or "date" in ds_fb.dims else "time"
                            t_da = ds_fb[fb_temp].sel({fb_time: slice(start, end)}).load()
                            if fb_time != "time":
                                t_da = t_da.rename({fb_time: "time"})
                            temp_from_fallback = _ensure_daily_time_index(
                                t_da.to_dataset(name="temperature_2m_mean"),
                                start=start,
                                end=end,
                            )["temperature_2m_mean"]
                            temp_src = "temperature_2m_mean"
                            print(f"Attached temperature from hydrodata fallback: {fallback_file.name}")
            if temp_src_used is None and temp_src is not None:
                temp_src_used = temp_src

            required = required_common + [pet_src]
            if temp_src is not None and temp_from_fallback is None:
                required.append(temp_src)
            missing = [v for v in required if v not in ds0.data_vars]
            if missing:
                raise KeyError(f"Missing variables in {ts_file}: {missing}")

            ds1 = ds0[required].sel({time_dim: slice(start, end)}).load()
            if time_dim != "time":
                ds1 = ds1.rename({time_dim: "time"})
            ds1 = _ensure_daily_time_index(ds1, start=start, end=end)

            data_vars = {
                "total_precipitation_sum": (("basin", "time"), ds1["total_precipitation_sum"].astype("float32").values[np.newaxis, :], {"units": "mm/day"}),
                "potential_evaporation_sum": (("basin", "time"), ds1[pet_src].astype("float32").values[np.newaxis, :], {"units": "mm/day"}),
                "streamflow": (("basin", "time"), ds1["streamflow"].astype("float32").values[np.newaxis, :], {"units": "mm/day"}),
            }
            if temp_from_fallback is not None:
                data_vars["temperature_2m_mean"] = (
                    ("basin", "time"),
                    temp_from_fallback.astype("float32").values[np.newaxis, :],
                    {"units": "degC"},
                )
            elif temp_src is not None:
                data_vars["temperature_2m_mean"] = (
                    ("basin", "time"),
                    ds1[temp_src].astype("float32").values[np.newaxis, :],
                    {"units": "degC"},
                )
            ds_out = xr.Dataset(
                data_vars=data_vars,
                coords={"basin": [bid], "time": ds1["time"].values},
            )
            out_list.append(ds_out)

    out_ds = xr.concat(out_list, dim="basin")

    first_id, last_id = basin_ids[0], basin_ids[-1]
    batch_path = cache_dir / f"caravan_{region_folder}_timeseries_batch_{first_id}_{last_id}.nc"
    if batch_path.exists():
        batch_path.unlink()
    out_ds.to_netcdf(batch_path)
    removed = _remove_overlapping_batch_caches(
        cache_dir, region_folder, basin_ids, keep_path=batch_path
    )
    print(f"Saved timeseries cache: {batch_path}")
    if removed:
        print(
            "Removed overlapping batch cache(s) (duplicate basin concat fix): "
            + ", ".join(p.name for p in removed)
        )

    # Minimal attributes cache (area only)
    attr_csv = caravan_root / "attributes" / region_folder / f"attributes_other_{region_folder}.csv"
    if not attr_csv.exists():
        raise FileNotFoundError(f"Attributes CSV not found (for area): {attr_csv}")

    df_attr = pd.read_csv(attr_csv)
    areas = []
    for bid in basin_ids:
        row = df_attr[df_attr["gauge_id"].astype(str) == bid]
        if row.empty:
            raise ValueError(f"Could not find gauge_id={bid} in {attr_csv}")
        areas.append(float(row.iloc[0]["area"]))
    new_attr = xr.Dataset(
        data_vars={"area": (("basin",), np.array(areas, dtype="float32"), {"units": "km^2"})},
        coords={"basin": basin_ids},
    )

    attr_cache = cache_dir / "caravan_attributes.nc"
    if attr_cache.exists():
        with xr.open_dataset(attr_cache) as existing:
            existing_mem = existing.load()
        combined = _merge_area_attrs(existing_mem, new_attr)
        combined.to_netcdf(attr_cache)
    else:
        new_attr.to_netcdf(attr_cache)
    print(f"Saved attributes cache: {attr_cache}")

    if pet_src_used:
        print(f"Using PET var: {pet_src_used}")
    if temp_src_used:
        print(f"Using temperature var: {temp_src_used} -> temperature_2m_mean")
    else:
        print("Warning: no temperature variable found; XAJ-Snow will not run on this cache.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

