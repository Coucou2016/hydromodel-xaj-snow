from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


def _detect_caravan_root(data_root: Path) -> Path:
    """
    Accept layouts:
    - <data_root>/CARAVAN/attributes|timeseries|shapefiles
    - <data_root>/CARAVAN/Caravan/Caravan/attributes|timeseries|shapefiles
    - <data_root>/attributes|timeseries|shapefiles (direct)
    """
    data_root = data_root.resolve()
    caravan_root = data_root / "CARAVAN"
    if caravan_root.exists():
        if (caravan_root / "Caravan" / "Caravan").exists():
            caravan_root = caravan_root / "Caravan" / "Caravan"
        elif (caravan_root / "attributes").exists():
            pass
        else:
            raise FileNotFoundError(f"Unrecognized CARAVAN layout under: {caravan_root}")
    else:
        if (data_root / "attributes").exists() and (data_root / "timeseries").exists():
            caravan_root = data_root
        else:
            raise FileNotFoundError(
                f"CARAVAN not found under: {data_root}. Expected <data_root>/CARAVAN/... or direct attributes/timeseries."
            )
    return caravan_root


def _pick_pet_var(ds: xr.Dataset, preference: str) -> str:
    pref = preference.strip().upper()
    candidates: list[str] = []
    if pref in {"FAO", "FAO_PM", "FAO_PENMAN_MONTEITH"}:
        candidates.append("potential_evaporation_sum_FAO_PENMAN_MONTEITH")
    if pref in {"ERA5", "ERA5_LAND"}:
        candidates.append("potential_evaporation_sum_ERA5_LAND")
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
    raise KeyError(f"PET variable not found. Tried: {candidates}")


def _time_dim(ds: xr.Dataset) -> str:
    if "date" in ds.coords or "date" in ds.dims:
        return "date"
    if "time" in ds.coords or "time" in ds.dims:
        return "time"
    raise KeyError("No 'date' or 'time' coordinate in dataset")


def _nan_frac(x: np.ndarray) -> float:
    if x.size == 0:
        return float("nan")
    return float(np.isnan(x).sum() / x.size)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    os.chdir(repo_root)

    p = argparse.ArgumentParser(
        description="Diagnose CARAVAN basin time alignment, missingness, and XAJ suitability features."
    )
    p.add_argument(
        "--data-root",
        required=True,
        help="Directory that contains CARAVAN folder (i.e., <data-root>/CARAVAN).",
    )
    p.add_argument("--region-folder", default="camels", help="Region folder under attributes/ and timeseries/netcdf/.")
    p.add_argument("--pet-preference", default="FAO_PENMAN_MONTEITH", help="FAO_PENMAN_MONTEITH or ERA5_LAND")
    p.add_argument("--basin-ids", nargs="+", required=True, help="Basin IDs (e.g., camels_01013500 ...)")
    p.add_argument("--train-period", nargs=2, default=["1985-10-01", "1995-09-30"], help="Train start end (YYYY-MM-DD)")
    p.add_argument("--test-period", nargs=2, default=["2005-10-01", "2014-09-30"], help="Test start end (YYYY-MM-DD)")
    p.add_argument("--out-csv", default="results/basin_diagnosis_report.csv", help="Output CSV path")
    args = p.parse_args()

    caravan_root = _detect_caravan_root(Path(args.data_root))
    region = str(args.region_folder)

    ts_dir = caravan_root / "timeseries" / "netcdf" / region
    attr_caravan = caravan_root / "attributes" / region / f"attributes_caravan_{region}.csv"
    attr_hydroatlas = caravan_root / "attributes" / region / f"attributes_hydroatlas_{region}.csv"
    attr_other = caravan_root / "attributes" / region / f"attributes_other_{region}.csv"

    if not attr_caravan.exists():
        raise FileNotFoundError(f"Missing: {attr_caravan}")
    if not attr_other.exists():
        raise FileNotFoundError(f"Missing: {attr_other}")

    df_feat = pd.read_csv(attr_caravan)
    df_other = pd.read_csv(attr_other)
    df_attr = df_other.merge(df_feat, on="gauge_id", how="left")

    # Optional: add a small set of HydroATLAS-derived attributes (many columns; keep only a few high-signal ones).
    hydro_cols = [
        "gauge_id",
        "pre_mm_syr",   # annual precipitation (mm/yr)
        "pet_mm_syr",   # annual PET (mm/yr)
        "aet_mm_syr",   # annual AET (mm/yr) (may be missing in some variants)
        "slp_dg_sav",   # mean slope (deg)
        "ele_mt_smx",   # max elevation (m)
        "for_pc_sse",   # forest %
        "crp_pc_sse",   # cropland %
        "ire_pc_sse",   # irrigation equipped area %
        "wet_pc_sg1",   # wetland %
        "hft_ix_s93",   # human footprint index
        "clz_cl_smj",   # climate zone class (categorical code)
    ]
    if attr_hydroatlas.exists():
        df_h = pd.read_csv(attr_hydroatlas, usecols=lambda c: c in set(hydro_cols))
        df_attr = df_attr.merge(df_h, on="gauge_id", how="left")

    train_start, train_end = args.train_period
    test_start, test_end = args.test_period

    rows: list[dict] = []
    for bid in args.basin_ids:
        bid = str(bid)
        ts_file = ts_dir / f"{bid}.nc"
        if not ts_file.exists():
            rows.append(
                {
                    "basin_id": bid,
                    "ok": False,
                    "error": f"missing_timeseries_file: {ts_file}",
                }
            )
            continue

        try:
            with xr.open_dataset(ts_file) as ds0:
                tdim = _time_dim(ds0)
                pet_var = _pick_pet_var(ds0, args.pet_preference)

                required = ["total_precipitation_sum", pet_var, "streamflow"]
                missing = [v for v in required if v not in ds0.data_vars]
                if missing:
                    raise KeyError(f"missing_vars: {missing}")

                ds = ds0[required]
                ds = ds.rename({tdim: "time"}) if tdim != "time" else ds

                t = pd.to_datetime(ds["time"].values)
                t_sorted = np.all(t[:-1] <= t[1:]) if len(t) > 1 else True

                # overall missingness (full available record)
                p_all = ds["total_precipitation_sum"].values.astype("float64")
                e_all = ds[pet_var].values.astype("float64")
                q_all = ds["streamflow"].values.astype("float64")

                # slice periods and compute missingness
                ds_train = ds.sel(time=slice(train_start, train_end))
                ds_test = ds.sel(time=slice(test_start, test_end))

                def _period_stats(dsp: xr.Dataset) -> dict:
                    if dsp.sizes.get("time", 0) == 0:
                        return {
                            "n_days": 0,
                            "p_nan_frac": float("nan"),
                            "e_nan_frac": float("nan"),
                            "q_nan_frac": float("nan"),
                        }
                    p = dsp["total_precipitation_sum"].values.astype("float64")
                    e = dsp[pet_var].values.astype("float64")
                    q = dsp["streamflow"].values.astype("float64")
                    return {
                        "n_days": int(dsp.sizes["time"]),
                        "p_nan_frac": _nan_frac(p),
                        "e_nan_frac": _nan_frac(e),
                        "q_nan_frac": _nan_frac(q),
                    }

                st_train = _period_stats(ds_train)
                st_test = _period_stats(ds_test)

                # A minimal "alignment" guarantee here is: same time axis inside a single basin netcdf.
                # We still report whether any variable has NaNs.
                first_day = str(pd.to_datetime(t.min()).date())
                last_day = str(pd.to_datetime(t.max()).date())

        except Exception as e:
            rows.append({"basin_id": bid, "ok": False, "error": str(e)})
            continue

        # attributes (optional)
        arow = df_attr[df_attr["gauge_id"].astype(str) == bid]
        if not arow.empty:
            a = arow.iloc[0].to_dict()
        else:
            a = {}

        # simple suitability flags
        frac_snow = a.get("frac_snow", np.nan)
        aridity = a.get("aridity_FAO_PM", np.nan)
        p_mean = a.get("p_mean", np.nan)
        area_km2 = a.get("area", np.nan)
        lat = a.get("gauge_lat", np.nan)
        lon = a.get("gauge_lon", np.nan)
        country = a.get("country", "")

        # HydroATLAS signals (optional)
        hft = a.get("hft_ix_s93", np.nan)
        ire = a.get("ire_pc_sse", np.nan)
        slp = a.get("slp_dg_sav", np.nan)
        for_pc = a.get("for_pc_sse", np.nan)
        crp_pc = a.get("crp_pc_sse", np.nan)

        flags = {
            "flag_low_snow": bool(frac_snow <= 0.1) if pd.notna(frac_snow) else False,
            "flag_humid_or_semi_humid": bool(aridity <= 1.5) if pd.notna(aridity) else False,
            "flag_has_full_train": st_train["n_days"] >= 3650,  # ~10 years
            "flag_has_full_test": st_test["n_days"] >= 3285,  # ~9 years
            "flag_low_missing_test": (
                (st_test["p_nan_frac"] <= 0.01)
                and (st_test["e_nan_frac"] <= 0.01)
                and (st_test["q_nan_frac"] <= 0.01)
            )
            if st_test["n_days"] > 0 and not any(pd.isna([st_test["p_nan_frac"], st_test["e_nan_frac"], st_test["q_nan_frac"]]))
            else False,
            "flag_low_human_footprint": bool(hft <= 15.0) if pd.notna(hft) else False,
            "flag_low_irrigation": bool(ire <= 2.0) if pd.notna(ire) else False,
        }

        # A simple suitability score for screening (higher = more likely XAJ-friendly, purely heuristic)
        score = int(sum(1 for v in flags.values() if bool(v)))

        rows.append(
            {
                "basin_id": bid,
                "ok": True,
                "first_day": first_day,
                "last_day": last_day,
                "time_sorted": bool(t_sorted),
                "pet_var": pet_var,
                "area_km2": area_km2,
                "gauge_lat": lat,
                "gauge_lon": lon,
                "country": country,
                "frac_snow": frac_snow,
                "aridity_FAO_PM": aridity,
                "p_mean_mm_day": p_mean,
                "hft_ix_s93": hft,
                "ire_pc_sse": ire,
                "slp_dg_sav": slp,
                "for_pc_sse": for_pc,
                "crp_pc_sse": crp_pc,
                "train_n_days": st_train["n_days"],
                "train_p_nan_frac": st_train["p_nan_frac"],
                "train_e_nan_frac": st_train["e_nan_frac"],
                "train_q_nan_frac": st_train["q_nan_frac"],
                "test_n_days": st_test["n_days"],
                "test_p_nan_frac": st_test["p_nan_frac"],
                "test_e_nan_frac": st_test["e_nan_frac"],
                "test_q_nan_frac": st_test["q_nan_frac"],
                **flags,
                "suitability_score": score,
                "error": "",
            }
        )

    df = pd.DataFrame(rows)

    # merge evaluation metrics if they exist (from our quick diag outputs)
    metric_files = list(Path("results/multi_basin_quick_diag").glob("*/xaj_mz_scipy/evaluation_test/basins_metrics.csv"))
    if metric_files:
        mrows = []
        for f in metric_files:
            d = pd.read_csv(f)
            basin = str(d.iloc[0, 0])
            mrows.append({"basin_id": basin, "NSE": float(d["NSE"].iloc[0]), "KGE": float(d["KGE"].iloc[0])})
        dfm = pd.DataFrame(mrows).drop_duplicates("basin_id")
        df = df.merge(dfm, on="basin_id", how="left")

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"Saved report: {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

