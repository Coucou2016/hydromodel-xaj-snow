"""
Portable helper to prepare CARAVAN under this repo's data folder.

By default, it only checks that CARAVAN is readable and prints some basin IDs.
Use --download to let hydrodataset download from Zenodo (large, may take long).
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    os.chdir(repo_root)

    p = argparse.ArgumentParser(description="Prepare CARAVAN under portable datasets-origin.")
    p.add_argument(
        "--download",
        action="store_true",
        help="Download/unzip CARAVAN if missing (large). If not set, only checks.",
    )
    p.add_argument(
        "--region",
        default="Global",
        help="Region for CARAVAN (Global/US/AUS/BR/CL/GB/NA/CE). Default: Global",
    )
    args = p.parse_args()

    from hydromodel import SETTING  # noqa: WPS433
    from hydrodataset.caravan import Caravan  # noqa: WPS433

    data_path = SETTING["local_data_path"]["datasets-origin"]
    print(f"Using datasets-origin: {data_path}")
    print(f"Requested CARAVAN region: {args.region}")

    # hydrodataset.Caravan will try to download if is_data_ready fails.
    # To support "check-only", we do a manual readiness check first.
    if not args.download:
        caravan_root = Path(data_path) / "CARAVAN"
        if not caravan_root.exists():
            raise FileNotFoundError(
                f"CARAVAN folder not found: {caravan_root}\n"
                f"Either place the extracted Caravan.zip into that folder, or re-run with --download."
            )

    ds = Caravan(data_path=data_path, region=args.region)
    basin_ids = ds.read_object_ids()
    print(f"CARAVAN ready. Basins available: {len(basin_ids)}")
    print(f"Example basin IDs: {basin_ids[:10]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

