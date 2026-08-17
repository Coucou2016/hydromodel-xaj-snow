"""Sanitize the frozen stratified sample for public release (Round 5).

Drops local absolute paths from sample_frozen.csv and sample_frozen_manifest.json,
keeps all basin identities/attributes/strata intact. Run once; outputs are committed.
"""
import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SAM = REPO / "results" / "sampling"
OUT = REPO / "results" / "diagnostics"


def main() -> None:
    df = pd.read_csv(SAM / "sample_frozen.csv")
    drop_cols = [
        c
        for c in df.columns
        if c
        in (
            "ts_path",
            "ts_exists",
            "avail_file",
            "nc_error",
            "avail_nc_checked",
            "avail_nc_ok",
        )
        or c.startswith("miss_")
    ]
    pub = df.drop(columns=drop_cols).copy()
    pub.to_csv(OUT / "sample_frozen_attributes.csv", index=False)

    with (SAM / "sample_frozen_manifest.json").open(encoding="utf-8") as f:
        man = json.load(f)
    man.pop("candidates_csv", None)
    man.pop("frozen_csv", None)
    man["frozen_sample_file"] = "results/diagnostics/sample_frozen_attributes.csv"
    man["caravan_variable_note"] = (
        "frac_snow, aridity (aridity_FAO_PM preferred), and degree-of-regulation "
        "taken from Caravan basin attribute tables; FAO Penman-Monteith PET forcing "
        "(Caravan >= v1.5) used for modeling."
    )
    with (OUT / "sample_frozen_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(man, f, indent=2, ensure_ascii=False)

    print(f"wrote {OUT/'sample_frozen_attributes.csv'} rows={len(pub)}")
    print(f"wrote {OUT/'sample_frozen_manifest.json'}")


if __name__ == "__main__":
    main()
