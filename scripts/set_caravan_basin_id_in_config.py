"""
Replace the placeholder basin id in configs/portable_caravan_global_quick.yaml.
This keeps the workflow non-interactive and PowerShell-friendly.
"""

from __future__ import annotations

import argparse
from pathlib import Path


PLACEHOLDER = "REPLACE_WITH_CARAVAN_BASIN_ID"


def main() -> int:
    p = argparse.ArgumentParser(description="Set CARAVAN basin id in portable config.")
    p.add_argument("--basin-id", required=True, help="CARAVAN basin/gauge id to use.")
    p.add_argument(
        "--config",
        default="configs/portable_caravan_global_quick.yaml",
        help="Path to config yaml to update.",
    )
    args = p.parse_args()

    cfg_path = Path(args.config)
    text = cfg_path.read_text(encoding="utf-8")
    if PLACEHOLDER not in text:
        raise ValueError(f"Placeholder '{PLACEHOLDER}' not found in {cfg_path}")

    basin_id = str(args.basin_id)
    new_text = text.replace(PLACEHOLDER, basin_id)
    n_replaced = text.count(PLACEHOLDER)
    cfg_path.write_text(new_text, encoding="utf-8")
    print(f"Updated {cfg_path} placeholder -> {basin_id} (replaced {n_replaced} occurrence(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

