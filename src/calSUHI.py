"""
calSUHI.py

Calculate Surface Urban Heat Island (SUHI) intensity for each
urban zone using MODIS Land Surface Temperature (LST).

For each urban zone, the script computes:
- Mean urban LST
- Mean rural LST
- SUHI intensity (Urban LST - Rural LST)

The results are exported as a GeoJSON file.
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask

# ============================================================
# Project directories
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"
RESULT_DIR = DATA_DIR / "results"

# ============================================================
# Input files
# ============================================================

lst_file = RAW_DIR / "MYD11A2_A2025_clipped_vn.tif"

smod_urban_file = INTERMEDIATE_DIR / "GHS_SMOD_urban_01_filtered.tif"

smod_rural_file = INTERMEDIATE_DIR / "GHS_SMOD_rural_01.tif"

urban_geojson = INTERMEDIATE_DIR / "urban_zones.geojson"

rural_geojson = INTERMEDIATE_DIR / "rural_zones.geojson"

# ============================================================
# Output file
# ============================================================

output_geojson = RESULT_DIR / "urban_zones_suhi.geojson"

# ============================================================
# Constants
# ============================================================

# MODIS MYD11A2 scale factor
LST_SCALE_FACTOR = 0.02

# ============================================================
# Read input data
# ============================================================

print("Loading input datasets...")

gdf_urban = gpd.read_file(urban_geojson)
gdf_rural = gpd.read_file(rural_geojson)

with (
    rasterio.open(lst_file) as src_lst,
    rasterio.open(smod_urban_file) as src_smod_u,
    rasterio.open(smod_rural_file) as src_smod_r,
):

    # Read raster arrays
    lst_raw = src_lst.read(1)
    smod_urban = src_smod_u.read(1)
    smod_rural = src_smod_r.read(1)

    # Raster metadata
    transform = src_lst.transform
    out_shape = src_lst.shape
    raster_crs = src_lst.crs

    # Convert MODIS digital numbers to Celsius
    valid_lst_mask = lst_raw > 0

    lst_celsius = np.where(
        valid_lst_mask,
        (lst_raw * LST_SCALE_FACTOR) - 273.15,
        np.nan,
    )

    # Reproject polygons to the raster CRS
    gdf_urban_reproj = gdf_urban.to_crs(raster_crs)
    gdf_rural_reproj = gdf_rural.to_crs(raster_crs)

    results = []

    print("Calculating SUHI for each urban zone...")

    # ========================================================
    # Process each urban zone
    # ========================================================

    for _, u_row in gdf_urban_reproj.iterrows():

        zone_id = u_row["zone_id"]

        # Find the corresponding rural zone
        r_match = gdf_rural_reproj[
            gdf_rural_reproj["zone_id"] == zone_id
        ]

        # ----------------------------------------------------
        # Urban LST
        # ----------------------------------------------------

        u_poly_mask = ~geometry_mask(
            [u_row.geometry],
            out_shape=out_shape,
            transform=transform,
            invert=False,
        )

        u_final_mask = (
            u_poly_mask
            & (smod_urban > 0)
            & (smod_urban != 255)
            & (~np.isnan(lst_celsius))
        )

        u_pixels_vals = lst_celsius[u_final_mask]

        u_count = len(u_pixels_vals)

        u_mean = (
            np.mean(u_pixels_vals)
            if u_count > 0
            else np.nan
        )

        # ----------------------------------------------------
        # Rural LST
        # ----------------------------------------------------

        r_count = 0
        r_mean = np.nan

        if not r_match.empty:

            r_geom = r_match.geometry.values[0]

            r_poly_mask = ~geometry_mask(
                [r_geom],
                out_shape=out_shape,
                transform=transform,
                invert=False,
            )

            r_final_mask = (
                r_poly_mask
                & (smod_rural > 0)
                & (smod_rural != 255)
                & (~np.isnan(lst_celsius))
            )

            r_pixels_vals = lst_celsius[r_final_mask]

            r_count = len(r_pixels_vals)

            r_mean = (
                np.mean(r_pixels_vals)
                if r_count > 0
                else np.nan
            )

        # ----------------------------------------------------
        # Calculate SUHI
        # ----------------------------------------------------

        suhi = (
            u_mean - r_mean
            if (
                not np.isnan(u_mean)
                and not np.isnan(r_mean)
            )
            else np.nan
        )

        results.append(
            {
                "zone_id": zone_id,
                "urban_pixels": int(u_count),
                "rural_pixels": int(r_count),
                "urban_mean_C": (
                    round(float(u_mean), 2)
                    if not np.isnan(u_mean)
                    else None
                ),
                "rural_mean_C": (
                    round(float(r_mean), 2)
                    if not np.isnan(r_mean)
                    else None
                ),
                "suhi_C": (
                    round(float(suhi), 2)
                    if not np.isnan(suhi)
                    else None
                ),
            }
        )

# ============================================================
# Create result table
# ============================================================

df_results = pd.DataFrame(results)

# ============================================================
# Merge results with the urban GeoDataFrame
# ============================================================

gdf_urban_updated = gdf_urban.merge(
    df_results,
    on="zone_id",
    how="left",
)

# ============================================================
# Export GeoJSON
# ============================================================

gdf_urban_updated.to_file(
    output_geojson,
    driver="GeoJSON",
)

# ============================================================
# Summary
# ============================================================

print("Surface Urban Heat Island (SUHI) calculation completed successfully.")
print(f"Output file : {output_geojson}")
print(f"Processed urban zones : {len(gdf_urban_updated)}")
