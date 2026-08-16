"""Build stratified Caravan sample across 7 regions for XAJ-Snow large-N work.

Merges attributes (frac_snow, aridity, dor, hft, area, precip), screens by
timeseries file existence (+ optional NC missingness checks), then freezes a
stratified sample with reproducible seed.

Outputs:
  results/sampling/stratified_candidates.csv
  results/sampling/sample_frozen.csv
  results/sampling/sample_frozen_manifest.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

REGIONS = ("camels", "camelsaus", "camelsbr", "camelscl", "camelsgb", "hysets", "lamah")

FOLDER_TO_REGION_CODE = {
    "camels": "US",
    "camelsaus": "AUS",
    "camelsbr": "BR",
    "camelscl": "CL",
    "camelsgb": "GB",
    "hysets": "NA",
    "lamah": "CE",
}


def _caravan_root(data_root: Path) -> Path:
    caravan = data_root / "CARAVAN"
    if (caravan / "Caravan" / "Caravan" / "attributes").exists():
        return caravan / "Caravan" / "Caravan"
    if (caravan / "attributes").exists():
        return caravan
    if (data_root / "attributes").exists():
        return data_root
    raise FileNotFoundError(f"CARAVAN attributes not found under {data_root}")


def _snow_bin(x: float) -> str:
    if not np.isfinite(x):
        return "unknown"
    if x < 0.1:
        return "S0_lt0.1"
    if x <= 0.3:
        return "S1_0.1_0.3"
    return "S2_gt0.3"


def _arid_bin(x: float) -> str:
    if not np.isfinite(x):
        return "unknown"
    if x < 0.75:
        return "A0_humid"
    if x < 1.25:
        return "A1_subhumid"
    return "A2_arid"


def _dor_bin(x: float) -> str:
    """Two-bin DOR: low vs elevated regulation."""
    if not np.isfinite(x):
        return "unknown"
    if x < 0.1:
        return "D0_lt0.1"
    return "D1_ge0.1"


def _load_region(root: Path, region: str) -> pd.DataFrame:
    other = root / "attributes" / region / f"attributes_other_{region}.csv"
    caravan = root / "attributes" / region / f"attributes_caravan_{region}.csv"
    hydro = root / "attributes" / region / f"attributes_hydroatlas_{region}.csv"
    if not other.exists():
        raise FileNotFoundError(other)

    df = pd.read_csv(other)
    for extra in (caravan, hydro):
        if extra.exists():
            d2 = pd.read_csv(extra)
            keep = [c for c in d2.columns if c == "gauge_id" or c not in df.columns]
            df = df.merge(d2[keep], on="gauge_id", how="left")

    out = pd.DataFrame()
    out["basin_id"] = df["gauge_id"].astype(str)
    out["region_folder"] = region
    out["region_code"] = FOLDER_TO_REGION_CODE.get(region, region)
    out["gauge_name"] = df["gauge_name"] if "gauge_name" in df.columns else ""
    out["country"] = df["country"] if "country" in df.columns else ""
    out["gauge_lat"] = pd.to_numeric(df.get("gauge_lat"), errors="coerce")
    out["gauge_lon"] = pd.to_numeric(df.get("gauge_lon"), errors="coerce")
    out["area_km2"] = pd.to_numeric(df.get("area"), errors="coerce")

    snow_col = next((c for c in ("frac_snow", "frac_snow_daily") if c in df.columns), None)
    arid_col = next(
        (c for c in ("aridity_FAO_PM", "aridity", "aridity_ERA5_LAND") if c in df.columns),
        None,
    )
    out["frac_snow"] = pd.to_numeric(df[snow_col], errors="coerce") if snow_col else np.nan
    out["aridity"] = pd.to_numeric(df[arid_col], errors="coerce") if arid_col else np.nan
    out["aridity_source"] = arid_col or ""
    out["dor_pc_pva"] = (
        pd.to_numeric(df["dor_pc_pva"], errors="coerce") if "dor_pc_pva" in df.columns else np.nan
    )
    out["hft_ix_s09"] = (
        pd.to_numeric(df["hft_ix_s09"], errors="coerce") if "hft_ix_s09" in df.columns else np.nan
    )
    out["hft_ix_s93"] = (
        pd.to_numeric(df["hft_ix_s93"], errors="coerce") if "hft_ix_s93" in df.columns else np.nan
    )
    out["pre_mm_syr"] = (
        pd.to_numeric(df["pre_mm_syr"], errors="coerce") if "pre_mm_syr" in df.columns else np.nan
    )

    ts_dir = root / "timeseries" / "netcdf" / region
    out["ts_path"] = out["basin_id"].map(lambda b: str(ts_dir / f"{b}.nc"))
    out["ts_exists"] = out["basin_id"].map(lambda b: (ts_dir / f"{b}.nc").exists())
    return out


def _period_missing_frac(
    nc_path: Path,
    start: str,
    end: str,
    vars_needed: tuple[str, ...],
) -> dict[str, float]:
    """Return missing fraction per variable over [start, end] (inclusive daily)."""
    import xarray as xr

    out: dict[str, float] = {}
    with xr.open_dataset(nc_path) as ds:
        time_dim = "date" if "date" in ds.dims or "date" in ds.coords else "time"
        # Map logical names to possible raw names
        aliases = {
            "P": ("total_precipitation_sum",),
            "E": (
                "potential_evaporation_sum_FAO_PENMAN_MONTEITH",
                "potential_evaporation_sum_ERA5_LAND",
                "potential_evaporation_sum",
            ),
            "T": ("temperature_2m_mean", "temperature_mean", "tmean", "tas"),
            "Q": ("streamflow",),
        }
        for logical in vars_needed:
            names = aliases.get(logical, (logical,))
            var = next((v for v in names if v in ds.data_vars), None)
            if var is None:
                out[f"miss_{logical}"] = 1.0
                continue
            da = ds[var].sel({time_dim: slice(start, end)})
            n = int(da.size)
            if n == 0:
                out[f"miss_{logical}"] = 1.0
            else:
                out[f"miss_{logical}"] = float(np.isnan(da.values).sum() / n)
    return out


def _screen_availability(
    df: pd.DataFrame,
    train: tuple[str, str],
    test: tuple[str, str],
    max_miss: float,
    sample_check: int,
    seed: int,
) -> pd.DataFrame:
    """File-existence filter for all; NC miss-rate check on a stratified sample."""
    ok = df[df["ts_exists"]].copy()
    ok["avail_file"] = True
    ok["avail_nc_checked"] = False
    ok["avail_nc_ok"] = pd.NA
    ok["nc_error"] = pd.NA
    for col in (
        "miss_P_train",
        "miss_E_train",
        "miss_T_train",
        "miss_Q_train",
        "miss_P_test",
        "miss_E_test",
        "miss_T_test",
        "miss_Q_test",
    ):
        ok[col] = np.nan

    if sample_check <= 0 or len(ok) == 0:
        return ok

    # Prefer checking across snow bins so screen is representative
    check_parts = []
    rng = np.random.default_rng(seed)
    for _, g in ok.groupby("snow_bin", dropna=False):
        n = min(len(g), max(1, sample_check // max(1, ok["snow_bin"].nunique())))
        idx = rng.choice(g.index.to_numpy(), size=n, replace=False)
        check_parts.append(ok.loc[idx])
    to_check = pd.concat(check_parts).drop_duplicates(subset=["basin_id"])
    # Cap total checks
    if len(to_check) > sample_check:
        to_check = to_check.sample(n=sample_check, random_state=seed)

    rows = []
    for _, row in to_check.iterrows():
        try:
            tr = _period_missing_frac(
                Path(row["ts_path"]), train[0], train[1], ("P", "E", "T", "Q")
            )
            te = _period_missing_frac(
                Path(row["ts_path"]), test[0], test[1], ("P", "E", "T", "Q")
            )
            rec = {
                "basin_id": row["basin_id"],
                "avail_nc_checked": True,
                "miss_P_train": tr["miss_P"],
                "miss_E_train": tr["miss_E"],
                "miss_T_train": tr["miss_T"],
                "miss_Q_train": tr["miss_Q"],
                "miss_P_test": te["miss_P"],
                "miss_E_test": te["miss_E"],
                "miss_T_test": te["miss_T"],
                "miss_Q_test": te["miss_Q"],
            }
            miss_vals = [v for k, v in rec.items() if k.startswith("miss_")]
            rec["avail_nc_ok"] = bool(all(v <= max_miss for v in miss_vals))
            rec["nc_error"] = ""
            rows.append(rec)
        except Exception as exc:  # noqa: BLE001 — record and continue
            rows.append(
                {
                    "basin_id": row["basin_id"],
                    "avail_nc_checked": True,
                    "avail_nc_ok": False,
                    "nc_error": str(exc),
                }
            )

    if rows:
        chk = pd.DataFrame(rows)
        drop_cols = [c for c in chk.columns if c != "basin_id" and c in ok.columns]
        ok = ok.drop(columns=drop_cols)
        ok = ok.merge(chk, on="basin_id", how="left")
        ok["avail_nc_checked"] = ok["avail_nc_checked"].fillna(False)
    return ok


def _stratified_sample(
    df: pd.DataFrame,
    n_target: int,
    seed: int,
    per_region_cap: int | None,
) -> pd.DataFrame:
    """Allocate across snow×aridity×dor strata with cross-region quotas."""
    work = df[
        df["ts_exists"]
        & df["snow_bin"].ne("unknown")
        & df["arid_bin"].ne("unknown")
        & df["dor_bin"].ne("unknown")
    ].copy()
    work["stratum"] = work["snow_bin"] + "|" + work["arid_bin"] + "|" + work["dor_bin"]

    strata = sorted(work["stratum"].unique())
    if not strata:
        return work.iloc[0:0].copy()

    # Equal share per stratum, then fill remainders
    base = max(1, n_target // len(strata))
    quota = {s: base for s in strata}
    rem = n_target - base * len(strata)
    rng = np.random.default_rng(seed)
    for s in rng.permutation(strata)[: max(0, rem)]:
        quota[s] += 1

    parts = []
    region_counts: dict[str, int] = {}
    for s in strata:
        g = work[work["stratum"] == s]
        # Prefer basins that passed NC check when available; else file-ok
        if "avail_nc_ok" in g.columns and g["avail_nc_ok"].notna().any():
            preferred = g[g["avail_nc_ok"] == True]  # noqa: E712
            if len(preferred) == 0:
                preferred = g
        else:
            preferred = g

        # Cross-region: sample with region balancing inside stratum
        take_n = min(quota[s], len(preferred))
        if take_n == 0:
            continue
        chosen_idx = []
        # Round-robin regions present in stratum
        by_reg = {r: list(idx) for r, idx in preferred.groupby("region_folder").groups.items()}
        for r in by_reg:
            rng.shuffle(by_reg[r])
        regs = list(by_reg.keys())
        rng.shuffle(regs)
        while len(chosen_idx) < take_n and any(by_reg[r] for r in regs):
            progressed = False
            for r in regs:
                if not by_reg[r]:
                    continue
                if per_region_cap is not None and region_counts.get(r, 0) >= per_region_cap:
                    by_reg[r] = []  # exhausted for this run
                    continue
                chosen_idx.append(by_reg[r].pop())
                region_counts[r] = region_counts.get(r, 0) + 1
                progressed = True
                if len(chosen_idx) >= take_n:
                    break
            if not progressed:
                break
        if chosen_idx:
            parts.append(preferred.loc[chosen_idx])

    if not parts:
        return work.iloc[0:0].copy()
    sampled = pd.concat(parts).drop_duplicates(subset=["basin_id"])
    # If under target, top-up randomly from remaining eligible
    if len(sampled) < n_target:
        rest = work[~work["basin_id"].isin(sampled["basin_id"])]
        need = n_target - len(sampled)
        if len(rest) and need > 0:
            extra = rest.sample(n=min(need, len(rest)), random_state=seed)
            sampled = pd.concat([sampled, extra], ignore_index=True)
    return sampled.reset_index(drop=True)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    p = argparse.ArgumentParser(description="Stratified Caravan sample for XAJ-Snow.")
    p.add_argument("--data-root", default=str(repo / "_portable_data" / "datasets-origin"))
    p.add_argument("--seed", type=int, default=20260816)
    p.add_argument("--n-candidates-note", type=int, default=500, help="Paper-scale aspirational N.")
    p.add_argument(
        "--n-freeze",
        type=int,
        default=80,
        help="Frozen runnable first batch size (60–120 recommended).",
    )
    p.add_argument("--per-region-cap", type=int, default=25)
    p.add_argument("--max-miss", type=float, default=0.15, help="Max missing fraction per var/period.")
    p.add_argument(
        "--nc-check-n",
        type=int,
        default=120,
        help="How many basins to open for NC missingness audit (0=skip).",
    )
    p.add_argument("--train-start", default="1985-10-01")
    p.add_argument("--train-end", default="1995-09-30")
    p.add_argument("--test-start", default="2005-10-01")
    p.add_argument("--test-end", default="2014-09-30")
    p.add_argument("--out-dir", default=str(repo / "results" / "sampling"))
    args = p.parse_args()

    root = _caravan_root(Path(args.data_root))
    frames = [_load_region(root, r) for r in REGIONS]
    all_df = pd.concat(frames, ignore_index=True)
    all_df["snow_bin"] = all_df["frac_snow"].apply(_snow_bin)
    all_df["arid_bin"] = all_df["aridity"].apply(_arid_bin)
    all_df["dor_bin"] = all_df["dor_pc_pva"].apply(_dor_bin)
    all_df["stratum"] = all_df["snow_bin"] + "|" + all_df["arid_bin"] + "|" + all_df["dor_bin"]

    screened = _screen_availability(
        all_df,
        train=(args.train_start, args.train_end),
        test=(args.test_start, args.test_end),
        max_miss=args.max_miss,
        sample_check=args.nc_check_n,
        seed=args.seed,
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cand_path = out_dir / "stratified_candidates.csv"
    screened.to_csv(cand_path, index=False)

    frozen = _stratified_sample(
        screened,
        n_target=args.n_freeze,
        seed=args.seed,
        per_region_cap=args.per_region_cap,
    )
    frozen["batch"] = "freeze_v1"
    frozen["seed"] = args.seed
    frozen["include_in_batch"] = True
    frozen_path = out_dir / "sample_frozen.csv"
    frozen.to_csv(frozen_path, index=False)

    stratum_counts = (
        frozen.groupby(["snow_bin", "arid_bin", "dor_bin", "region_folder"])
        .size()
        .reset_index(name="n")
        .to_dict(orient="records")
        if len(frozen)
        else []
    )
    manifest = {
        "seed": args.seed,
        "n_candidates_total": int(len(screened)),
        "n_ts_exists": int(screened["ts_exists"].sum()),
        "n_frozen": int(len(frozen)),
        "n_paper_target_note": int(args.n_candidates_note),
        "train_period": [args.train_start, args.train_end],
        "test_period": [args.test_start, args.test_end],
        "max_miss": args.max_miss,
        "nc_check_n": args.nc_check_n,
        "nc_checked_ok": int((screened["avail_nc_ok"] == True).sum())  # noqa: E712
        if "avail_nc_ok" in screened.columns
        else 0,
        "per_region_cap": args.per_region_cap,
        "snow_bins": "<0.1 / 0.1-0.3 / >0.3",
        "arid_bins": "<0.75 / 0.75-1.25 / >=1.25 (FAO_PM preferred)",
        "dor_bins": "<0.1 / >=0.1",
        "expansion_path": (
            "Re-run with --n-freeze 300..500 after first batch metrics land; "
            "keep same --seed for nested expansion, or bump seed and document."
        ),
        "region_counts_frozen": frozen["region_folder"].value_counts().to_dict()
        if len(frozen)
        else {},
        "snow_bin_counts_frozen": frozen["snow_bin"].value_counts().to_dict()
        if len(frozen)
        else {},
        "stratum_region_counts": stratum_counts,
        "candidates_csv": str(cand_path.as_posix()),
        "frozen_csv": str(frozen_path.as_posix()),
    }
    man_path = out_dir / "sample_frozen_manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    md = out_dir / "sampling_design.md"
    md.write_text(
        "\n".join(
            [
                "# Stratified sampling design (XAJ-Snow large-N)",
                "",
                f"- Seed: `{args.seed}`",
                f"- Candidates (all regions, attributes merged): `{len(screened)}`",
                f"- With timeseries file present: `{int(screened['ts_exists'].sum())}`",
                f"- Frozen first batch: `{len(frozen)}` → `{frozen_path.as_posix()}`",
                f"- Paper-scale target (not all run yet): {args.n_candidates_note}",
                "",
                "## Screening rules",
                f"- Train: {args.train_start}–{args.train_end}; test: {args.test_start}–{args.test_end}",
                f"- Require NC file under `timeseries/netcdf/<region>/`",
                f"- NC missingness audit on up to {args.nc_check_n} basins; max miss/var = {args.max_miss}",
                "- Strata: frac_snow × aridity × dor (3×3×2), cross-region quota with per-region cap",
                "",
                "## Frozen region counts",
                "```",
                json.dumps(manifest["region_counts_frozen"], indent=2, ensure_ascii=False),
                "```",
                "",
                "## Frozen snow-bin counts",
                "```",
                json.dumps(manifest["snow_bin_counts_frozen"], indent=2, ensure_ascii=False),
                "```",
                "",
                "## Expansion path",
                manifest["expansion_path"],
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(json.dumps({k: manifest[k] for k in ("n_candidates_total", "n_ts_exists", "n_frozen", "region_counts_frozen", "snow_bin_counts_frozen")}, indent=2))
    print(f"Wrote {cand_path}")
    print(f"Wrote {frozen_path}")
    print(f"Wrote {man_path}")
    print(f"Wrote {md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
