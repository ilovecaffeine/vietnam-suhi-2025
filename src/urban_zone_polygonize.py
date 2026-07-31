"""
urban_zone_polygonize.py

Convert the urban ID raster into urban zone polygons and
export the result as a GeoJSON file.

Each polygon represents one urban zone and includes:
- Zone ID
- Zone type
- Area (km²)
- Representative longitude and latitude
"""

from pathlib import Path

import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape

# ============================================================
# Project directories
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"

# ============================================================
# Input and output files
# ============================================================

raster_path = INTERMEDIATE_DIR / "GHS_SMOD_urban_id.tif"

geojson_output_path = INTERMEDIATE_DIR / "urban_zones.geojson"

# ============================================================
# Read urban ID raster
# ============================================================

print("Converting urban ID raster to polygons...")

with rasterio.open(raster_path) as src:

    image = src.read(1)

    mask = (
        (image != src.nodata)
        & (image > 0)
    )

    transform = src.transform
    crs = src.crs

# ============================================================
# Polygonize raster
# ============================================================

records = []

for geom, value in shapes(
    image,
    mask=mask,
    transform=transform,
):

    records.append(
        {
            "geometry": shape(geom),
            "zone_id": int(value),
            "zone_type": "urban",
        }
    )

# ============================================================
# Create GeoDataFrame
# ============================================================

gdf = gpd.GeoDataFrame(
    records,
    crs=crs,
)

# Merge polygons with the same urban ID
gdf = gdf.dissolve(
    by=[
        "zone_id",
        "zone_type",
    ],
    as_index=False,
)

# ============================================================
# Repair invalid geometries
# ============================================================

try:

    gdf["geometry"] = gdf.geometry.make_valid()

except AttributeError:

    # Compatible with Shapely < 2.0
    gdf["geometry"] = gdf.buffer(0)

# ============================================================
# Calculate polygon area (km²)
# ============================================================

gdf["area_km2"] = gdf.area / 1_000_000

# ============================================================
# Calculate representative coordinates
# ============================================================

rep_points = gpd.GeoSeries(
    gdf.geometry.representative_point(),
    crs=crs,
).to_crs(
    epsg=4326,
)

gdf["centroid_lon"] = rep_points.x.round(6)
gdf["centroid_lat"] = rep_points.y.round(6)

# ============================================================
# Reproject to WGS84
# ============================================================

gdf = gdf.to_crs(
    epsg=4326,
)

# ============================================================
# Set output data types
# ============================================================

gdf["zone_id"] = gdf["zone_id"].astype(int)

gdf["area_km2"] = (
    gdf["area_km2"]
    .astype(float)
    .round(2)
)

# ============================================================
# Export GeoJSON
# ============================================================

gdf.to_file(
    geojson_output_path,
    driver="GeoJSON",
)

# ============================================================
# Summary
# ============================================================

print("Urban zone polygons created successfully.")
print(f"Output file : {geojson_output_path}")
print(f"Urban zones : {len(gdf)}")

print("\nPreview:")

print(
    gdf[
        [
            "zone_id",
            "zone_type",
            "area_km2",
            "centroid_lon",
            "centroid_lat",
        ]
    ].head()
)