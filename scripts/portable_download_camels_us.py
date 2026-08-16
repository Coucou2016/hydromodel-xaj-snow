"""
Portable helper to download/initialize CAMELS-US under this repo's data folder.

This script reads data root from ./hydro_setting.yml (repo root) via hydromodel.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> int:
    # Ensure we run with repo root as cwd when invoked from elsewhere
    repo_root = Path(__file__).resolve().parents[1]
    os.chdir(repo_root)

    parser = argparse.ArgumentParser(description="Prepare CAMELS-US under portable datasets-origin.")
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download/extract CAMELS-US if missing (may take long). If not set, only checks.",
    )
    args = parser.parse_args()

    from hydromodel import SETTING  # noqa: WPS433
    from hydrodataset.camels_us import CamelsUs  # noqa: WPS433

    data_path = SETTING["local_data_path"]["datasets-origin"]
    print(f"Using datasets-origin: {data_path}")

    # If download is False, this will only work if data is already prepared.
    ds = CamelsUs(data_path=data_path, download=bool(args.download))
    basin_ids = ds.read_object_ids()
    print(f"CAMELS-US ready. Basins available: {len(basin_ids)}")
    print(f"Example basin IDs: {basin_ids[:10]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

