"""
Plot a real basin overview map for public datasets (CAMELS-US / CARAVAN) using
the shapefiles shipped with those datasets.

Notes:
- CAMELS-US provides basin boundary polygons (no river network). We plot basin + gauge point.
- CARAVAN provides basin boundary shapefiles. River network is not included in the base ZIP.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser(description="Plot basin map for CAMELS-US / CARAVAN.")
    p.add_argument("--dataset", required=True, choices=["camels_us", "caravan"], help="Public dataset name.")
    p.add_argument("--basin-id", required=True, help="Basin / gauge ID.")
    p.add_argument("--output", required=True, help="Output PNG path.")
    p.add_argument(
        "--region",
        default="Global",
        help="Caravan region (Global/US/AUS/BR/CL/GB/NA/CE) or region folder name (camels/camelsaus/...).",
    )
    return p.parse_args()


def _find_id_column(gdf, basin_id: str) -> str | None:
    candidates = [
        "GAGE_ID",
        "gage_id",
        "gauge_id",
        "station_id",
        "STATION_ID",
        "BASIN_ID",
        "basin_id",
        "hru_id",
        "Hru_id",
    ]
    for c in candidates:
        if c in gdf.columns:
            return c
    # fallback: find any object column containing basin_id
    for c in gdf.columns:
        if gdf[c].dtype == object:
            try:
                if (gdf[c].astype(str) == str(basin_id)).any():
                    return c
            except Exception:
                continue
    return None


def _plot(gdf_basin, gauge_point=None, title: str = ""):
    import geopandas as gpd  # noqa: WPS433
    import matplotlib.pyplot as plt  # noqa: WPS433

    fig, ax = plt.subplots(figsize=(7, 6))
    gdf_basin.plot(ax=ax, color="#cfe8ff", alpha=0.6)
    gdf_basin.boundary.plot(ax=ax, color="#1f4e79", linewidth=2)
    if gauge_point is not None:
        gpd.GeoSeries([gauge_point], crs=gdf_basin.crs).plot(
            ax=ax, color="#d62728", markersize=60, marker="^", label="Gauge"
        )
        ax.legend(loc="best")
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return fig


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    os.chdir(repo_root)

    try:
        import geopandas as gpd  # noqa: WPS433
        import matplotlib.pyplot as plt  # noqa: WPS433
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "Missing plotting dependency. Please run inside the `hydromodel` environment "
            "and ensure `geopandas` + `matplotlib` are installed."
        ) from e

    from hydromodel import SETTING  # noqa: WPS433

    datasets_origin = Path(SETTING["local_data_path"]["datasets-origin"])

    basin_id = str(args.basin_id)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.dataset == "camels_us":
        # aqua_fetch stores CAMELS-US under <datasets-origin>/CAMELS_US/
        shp = datasets_origin / "CAMELS_US" / "basin_set_full_res" / "HCDN_nhru_final_671.shp"
        if not shp.exists():
            raise FileNotFoundError(
                f"CAMELS-US boundary shapefile not found: {shp}\n"
                f"Please prepare CAMELS-US under: {datasets_origin / 'CAMELS_US'}"
            )
        gdf = gpd.read_file(shp)
        id_col = _find_id_column(gdf, basin_id)
        if id_col:
            gdf_basin = gdf[gdf[id_col].astype(str) == basin_id]
        else:
            gdf_basin = gdf
        if gdf_basin.empty:
            raise ValueError(f"Basin id not found in shapefile ({id_col}): {basin_id}")
        # CAMELS doesn't ship "gauge point" shapefile; use centroid for a map marker.
        gauge_point = gdf_basin.geometry.iloc[0].centroid
        fig = _plot(gdf_basin, gauge_point=gauge_point, title=f"CAMELS-US basin {basin_id}")
        fig.savefig(out, dpi=200)
        plt.close(fig)
        print(f"Saved: {out}")
        return 0

    # caravan
    caravan_root = datasets_origin / "CARAVAN"
    if not caravan_root.exists():
        raise FileNotFoundError(f"CARAVAN folder not found: {caravan_root}")

    caravan_region = str(args.region)
    region_folder_map = {
        # Accept both dataset-style region codes and the folder names used in Caravan.zip
        "US": "camels",
        "AUS": "camelsaus",
        "BR": "camelsbr",
        "CL": "camelscl",
        "GB": "camelsgb",
        "NA": "hysets",
        "CE": "lamah",
    }

    shp_dir = caravan_root / "shapefiles"
    if caravan_region and caravan_region != "Global":
        shp_dir = shp_dir / region_folder_map.get(caravan_region, caravan_region)
    shp_files = list(shp_dir.glob("*.shp"))
    if len(shp_files) != 1:
        raise FileNotFoundError(f"Expected exactly 1 shapefile in {shp_dir}, found {len(shp_files)}")
    shp = shp_files[0]

    gdf = gpd.read_file(shp)
    id_col = _find_id_column(gdf, basin_id)
    if id_col:
        gdf_basin = gdf[gdf[id_col].astype(str) == basin_id]
    else:
        gdf_basin = gdf
    if gdf_basin.empty:
        raise ValueError(f"Basin id not found in Caravan shapefile ({id_col}): {basin_id}")

    # Prefer true gauge coordinates if available (attributes_other_<region>.csv has gauge_lat/gauge_lon for CARAVAN subsets)
    gauge_point = None
    try:
        import pandas as pd  # noqa: WPS433
        from shapely.geometry import Point  # noqa: WPS433

        region_folder = region_folder_map.get(caravan_region, caravan_region)
        attr_other = caravan_root / "attributes" / region_folder / f"attributes_other_{region_folder}.csv"
        if attr_other.exists():
            df = pd.read_csv(attr_other)
            row = df[df["gauge_id"].astype(str) == basin_id]
            if not row.empty and "gauge_lat" in row.columns and "gauge_lon" in row.columns:
                lat = float(row.iloc[0]["gauge_lat"])
                lon = float(row.iloc[0]["gauge_lon"])
                gauge_point = Point(lon, lat)
    except Exception:
        gauge_point = None

    if gauge_point is None:
        # Fallback: centroid (only for schematic use)
        gauge_point = gdf_basin.geometry.iloc[0].centroid

    fig = _plot(
        gdf_basin,
        gauge_point=gauge_point,
        title=f"CARAVAN basin {basin_id} ({args.region})",
    )
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"Saved: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

