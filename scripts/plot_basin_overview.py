"""
Plot a paper-style basin overview map for a selfmadehydrodataset:
- Basin boundary polygon (shapes/basins.shp, column BASIN_ID)
- River network (optional, shapes/rivers.shp)
- Gauge location (optional, shapes/gauges.shp)

Outputs a PNG figure.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt


def parse_args():
    p = argparse.ArgumentParser(description="Plot basin overview map (boundary/river/gauge).")
    p.add_argument("--dataset-name", required=True, help="Folder name under basins-origin (e.g., demo_selfmade)")
    p.add_argument("--basin-id", required=True, help="Basin ID (matches BASIN_ID / BASIN_ID field)")
    p.add_argument("--output", required=True, help="Output PNG path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    os.chdir(repo_root)

    from hydromodel import SETTING  # noqa: WPS433

    basins_root = Path(SETTING["local_data_path"]["basins-origin"])
    ds_root = basins_root / args.dataset_name
    shapes_dir = ds_root / "shapes"

    basins_shp = shapes_dir / "basins.shp"
    rivers_shp = shapes_dir / "rivers.shp"
    gauges_shp = shapes_dir / "gauges.shp"

    if not basins_shp.exists():
        raise FileNotFoundError(f"Missing basin shapefile: {basins_shp}")

    gdf_basin = gpd.read_file(basins_shp)
    if "BASIN_ID" in gdf_basin.columns:
        gdf_basin = gdf_basin[gdf_basin["BASIN_ID"].astype(str) == str(args.basin_id)]
    elif "basin_id" in gdf_basin.columns:
        gdf_basin = gdf_basin[gdf_basin["basin_id"].astype(str) == str(args.basin_id)]

    if gdf_basin.empty:
        raise ValueError(f"Basin not found in {basins_shp}: {args.basin_id}")

    gdf_river = None
    if rivers_shp.exists():
        gdf_river = gpd.read_file(rivers_shp)
        if "BASIN_ID" in gdf_river.columns:
            gdf_river = gdf_river[gdf_river["BASIN_ID"].astype(str) == str(args.basin_id)]

    gdf_gauge = None
    if gauges_shp.exists():
        gdf_gauge = gpd.read_file(gauges_shp)
        if "BASIN_ID" in gdf_gauge.columns:
            gdf_gauge = gdf_gauge[gdf_gauge["BASIN_ID"].astype(str) == str(args.basin_id)]

    # Plot
    fig, ax = plt.subplots(figsize=(7, 6))
    gdf_basin.boundary.plot(ax=ax, color="#1f4e79", linewidth=2, label="Basin boundary")
    gdf_basin.plot(ax=ax, color="#cfe8ff", alpha=0.6)

    if gdf_river is not None and not gdf_river.empty:
        gdf_river.plot(ax=ax, color="#0b6aa2", linewidth=2.2, label="River network")

    if gdf_gauge is not None and not gdf_gauge.empty:
        gdf_gauge.plot(ax=ax, color="#d62728", markersize=60, marker="^", label="Gauge")

    ax.set_title(f"Basin overview: {args.basin_id}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"Saved basin overview map: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

