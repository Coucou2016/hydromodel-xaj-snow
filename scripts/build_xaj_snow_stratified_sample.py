"""Build a stratified Caravan-CAMELS sample skeleton for later XAJ-Snow batch work.

Does NOT run calibration. Writes a CSV of candidate basins stratified by
frac_snow / aridity / DOR and CAMELS hydrologic region (HUC2 if available).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def _caravan_root(data_root: Path) -> Path:
    caravan = data_root / "CARAVAN"
    if (caravan / "Caravan" / "Caravan" / "attributes").exists():
        return caravan / "Caravan" / "Caravan"
    if (caravan / "attributes").exists():
        return caravan
    raise FileNotFoundError(f"CARAVAN attributes not found under {data_root}")


def _snow_bin(x: float) -> str:
    if not np.isfinite(x):
        return "unknown"
    if x < 0.05:
        return "S0_low"
    if x < 0.20:
        return "S1_mod"
    if x < 0.40:
        return "S2_high"
    return "S3_veryhigh"


def _arid_bin(x: float) -> str:
    if not np.isfinite(x):
        return "unknown"
    if x < 0.75:
        return "A0_humid"
    if x < 1.25:
        return "A1_subhumid"
    return "A2_arid"


def _dor_bin(x: float) -> str:
    if not np.isfinite(x):
        return "unknown"
    if x < 0.1:
        return "D0_low"
    if x < 0.5:
        return "D1_mid"
    return "D2_high"


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    p = argparse.ArgumentParser(description="Stratified sample skeleton (no calibration).")
    p.add_argument("--data-root", default=str(repo / "_portable_data" / "datasets-origin"))
    p.add_argument("--per-stratum", type=int, default=4, help="Basins per snow×aridity×region cell.")
    p.add_argument(
        "--output",
        default=str(repo / "results" / "diagnostics" / "xaj_snow_stratified_sample_skeleton.csv"),
    )
    args = p.parse_args()

    root = _caravan_root(Path(args.data_root))
    other = root / "attributes" / "camels" / "attributes_other_camels.csv"
    hydroatlas = root / "attributes" / "camels" / "attributes_hydroatlas_camels.csv"
    caravan_attr = root / "attributes" / "camels" / "attributes_caravan_camels.csv"
    if not other.exists():
        raise FileNotFoundError(other)

    df = pd.read_csv(other)
    for extra in (hydroatlas, caravan_attr):
        if extra.exists():
            d2 = pd.read_csv(extra)
            if "gauge_id" in d2.columns:
                df = df.merge(d2, on="gauge_id", how="left", suffixes=("", "_dup"))

    # Prefer Caravan climate indices if present
    snow_col = next((c for c in ("frac_snow", "frac_snow_daily") if c in df.columns), None)
    arid_col = next(
        (c for c in ("aridity_FAO_PM", "aridity", "aridity_era5") if c in df.columns),
        None,
    )
    dor_col = next((c for c in ("dor_pc_pva", "dor", "dor_pc_sse") if c in df.columns), None)
    region_col = next((c for c in ("huc_02", "huc02", "gauge_huc") if c in df.columns), None)

    out = pd.DataFrame()
    out["basin_id"] = df["gauge_id"].astype(str)
    out["frac_snow"] = df[snow_col] if snow_col else np.nan
    out["aridity"] = df[arid_col] if arid_col else np.nan
    out["dor"] = df[dor_col] if dor_col else np.nan
    if region_col:
        out["region"] = df[region_col].astype(str)
    else:
        # 7-region fallback from longitude if HUC missing
        lon = df["gauge_lon"] if "gauge_lon" in df.columns else np.nan
        out["region"] = pd.cut(
            lon,
            bins=[-130, -115, -105, -95, -85, -75, -66, 180],
            labels=["R1_west", "R2_interiorW", "R3_rockies", "R4_plains", "R5_midwest", "R6_appalachia", "R7_east"],
        ).astype(str)

    out["snow_bin"] = out["frac_snow"].apply(_snow_bin)
    out["arid_bin"] = out["aridity"].apply(_arid_bin)
    out["dor_bin"] = out["dor"].apply(_dor_bin)
    out["stratum"] = out["region"] + "|" + out["snow_bin"] + "|" + out["arid_bin"]

    parts = []
    for _, g in out.groupby("stratum"):
        n = min(len(g), args.per_stratum)
        parts.append(g.sample(n=n, random_state=1234))
    sampled = pd.concat(parts, ignore_index=True)
    sampled["include_in_batch"] = True
    sampled["note"] = "skeleton only; do not run 300-basin calibration in this round"

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sampled.to_csv(out_path, index=False)
    print(f"Wrote {out_path} n={len(sampled)} strata={sampled['stratum'].nunique()}")
    print("Columns used:", {"snow": snow_col, "aridity": arid_col, "dor": dor_col, "region": region_col})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
