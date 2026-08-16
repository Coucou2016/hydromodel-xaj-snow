"""
Generate a tiny selfmadehydrodataset demo under this repo for a fully-offline,
portable end-to-end run (calibrate -> evaluate -> visualize).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    os.chdir(repo_root)

    from hydromodel import SETTING  # noqa: WPS433

    basins_root = Path(SETTING["local_data_path"]["basins-origin"])
    cache_dir = Path(SETTING["local_data_path"].get("cache", basins_root.parent / ".cache"))
    dataset_name = "demo_selfmade"
    ds_root = basins_root / dataset_name

    attributes_dir = ds_root / "attributes"
    shapes_dir = ds_root / "shapes"
    timeseries_dir = ds_root / "timeseries" / "1D"
    ds_root.mkdir(parents=True, exist_ok=True)
    attributes_dir.mkdir(parents=True, exist_ok=True)
    shapes_dir.mkdir(parents=True, exist_ok=True)
    timeseries_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    basin_id = "basin_001"

    # -------------------------
    # shapes (basin polygon + river + gauge)
    # -------------------------
    # Make a simple synthetic basin in EPSG:4326 for demo/paper-style plotting.
    # (For real studies, replace these with your true basin boundary + river network + gauge location.)
    basins_shp = shapes_dir / "basins.shp"
    rivers_shp = shapes_dir / "rivers.shp"
    gauges_shp = shapes_dir / "gauges.shp"

    if not basins_shp.exists():
        # A rough polygon (lon/lat). Chosen to look like a plausible watershed outline.
        basin_poly = Polygon(
            [
                (120.00, 30.00),
                (120.35, 30.10),
                (120.55, 30.35),
                (120.40, 30.60),
                (120.10, 30.55),
                (119.90, 30.30),
            ]
        )
        gdf_basin = gpd.GeoDataFrame(
            [{"BASIN_ID": basin_id}],
            geometry=[basin_poly],
            crs="EPSG:4326",
        )
        gdf_basin.to_file(basins_shp)

    if not rivers_shp.exists():
        # A simple "main channel" line from upstream to outlet inside the polygon
        river = LineString(
            [
                (120.45, 30.55),
                (120.32, 30.48),
                (120.25, 30.40),
                (120.18, 30.33),
                (120.12, 30.22),
            ]
        )
        gdf_river = gpd.GeoDataFrame(
            [{"RIVER_ID": "river_001", "BASIN_ID": basin_id}],
            geometry=[river],
            crs="EPSG:4326",
        )
        gdf_river.to_file(rivers_shp)

    if not gauges_shp.exists():
        # Put a gauge at the downstream outlet end of the river
        gauge_pt = Point(120.12, 30.22)
        gdf_gauge = gpd.GeoDataFrame(
            [{"STATION_ID": "gauge_001", "BASIN_ID": basin_id}],
            geometry=[gauge_pt],
            crs="EPSG:4326",
        )
        gdf_gauge.to_file(gauges_shp)

    # -------------------------
    # attributes.csv
    # -------------------------
    attr_path = attributes_dir / "attributes.csv"
    if not attr_path.exists():
        df_attr = pd.DataFrame(
            [
                {
                    "basin_id": basin_id,
                    "area": 1000.0,  # km^2
                }
            ]
        )
        df_attr.to_csv(attr_path, index=False)

    # -------------------------
    # timeseries
    # -------------------------
    ts_path = timeseries_dir / f"{basin_id}.csv"
    if not ts_path.exists():
        rng = np.random.default_rng(1234)

        # 6 years of daily data
        time = pd.date_range("2000-01-01", "2005-12-31", freq="D")

        # Simple synthetic forcing
        prcp = rng.gamma(shape=0.8, scale=6.0, size=len(time))  # mm/day
        prcp[rng.random(len(time)) < 0.55] = 0.0  # many dry days

        pet = 2.0 + 2.0 * np.sin(2 * np.pi * (time.dayofyear / 365.25))  # mm/day
        pet = np.clip(pet, 0.0, None)

        # Very simple "flow" proxy (not hydrologically perfect, but stable/non-negative)
        q = np.zeros(len(time), dtype=float)
        k = 0.93
        for i in range(1, len(time)):
            q[i] = k * q[i - 1] + 0.12 * prcp[i] - 0.03 * pet[i]
        q = np.clip(q, 0.0, None)

        df_ts = pd.DataFrame(
            {
                "time": time.strftime("%Y-%m-%d"),
                "prcp": prcp.round(4),
                "PET": pet.round(4),
                "streamflow": q.round(4),
            }
        )
        df_ts.to_csv(ts_path, index=False)

    # -------------------------
    # units info
    # -------------------------
    units_path = ds_root / "timeseries" / "1D_units_info.json"
    if not units_path.exists():
        units = {
            "prcp": "mm/day",
            "PET": "mm/day",
            # Keep streamflow in mm/day for simplicity (avoids unit conversion needs)
            "streamflow": "mm/day",
        }
        units_path.write_text(json.dumps(units, indent=2), encoding="utf-8")

    # -------------------------
    # Pre-build hydrodatasource cache NetCDFs (avoid first-run caching issues)
    # -------------------------
    try:
        from hydrodatasource.reader.data_source import CACHE_DIR  # noqa: WPS433

        cache_path = Path(CACHE_DIR)
        cache_path.mkdir(parents=True, exist_ok=True)

        # Load the CSV we just generated to ensure dtypes are clean numeric
        df = pd.read_csv(ts_path)
        time = pd.to_datetime(df["time"]).to_numpy(dtype="datetime64[ns]")
        basin = np.array([basin_id], dtype=str)

        ts_ds = xr.Dataset(
            data_vars={
                "prcp": (["basin", "time"], df["prcp"].to_numpy()[None, :], {"units": "mm/day"}),
                "PET": (["basin", "time"], df["PET"].to_numpy()[None, :], {"units": "mm/day"}),
                "streamflow": (["basin", "time"], df["streamflow"].to_numpy()[None, :], {"units": "mm/day"}),
            },
            coords={"basin": basin, "time": time},
        )

        prefix = f"{dataset_name}_"
        ts_cache_file = cache_path / f"{prefix}timeseries_1D_batch_{basin_id}_{basin_id}.nc"
        ts_ds.to_netcdf(ts_cache_file)

        attr_ds = xr.Dataset(
            data_vars={"area": (["basin"], np.array([1000.0], dtype=float), {"units": "km^2"})},
            coords={"basin": basin},
        )
        attr_cache_file = cache_path / f"{prefix}attributes.nc"
        attr_ds.to_netcdf(attr_cache_file)
    except Exception as e:
        print(f"Warning: failed to build hydrodatasource cache files: {e}")

    print(f"Demo dataset ready: {ds_root}")
    print(f"- attributes: {attr_path}")
    print(f"- shapes: {shapes_dir}")
    print(f"- timeseries: {ts_path}")
    print(f"- units: {units_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

