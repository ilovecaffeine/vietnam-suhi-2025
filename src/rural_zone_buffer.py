"""
rural_zone_buffer.py

Generate rural zones as ring buffers surrounding urban zones.

Each rural zone is defined as:
- Outer buffer: 10 km
- Inner buffer: 2 km
- Existing urban areas are excluded from the final geometry.
"""

from pathlib import Path

import geopandas as gpd

# ============================================================
# Project directories
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"

# ============================================================
# Input and output files
# ============================================================

input_file = INTERMEDIATE_DIR / "urban_zones.geojson"

output_file = INTERMEDIATE_DIR / "rural_zones.geojson"

# ============================================================
# Coordinate reference system
# ============================================================

METRIC_CRS = "EPSG:32648"

# ============================================================
# Generate rural zones
# ============================================================

try:

    print("Generating rural zones...")

    gdf = gpd.read_file(input_file)

    # Reproject to a projected CRS (meters)
    gdf = gdf.to_crs(METRIC_CRS)

    # Merge all urban polygons into a single geometry
    urban_union = gdf.geometry.union_all()

    rural_features = []

    print("Creating 2–10 km ring buffers...")

    for _, row in gdf.iterrows():

        urban_geom = row.geometry

        # Outer buffer (10 km)
        outer = urban_geom.buffer(10000)

        # Inner buffer (2 km)
        inner = urban_geom.buffer(2000)

        # Create ring buffer
        ring = outer.difference(inner)

        # Remove all urban areas
        ring = ring.difference(urban_union)

        # Repair invalid geometries
        try:

            ring = ring.make_valid()

        except AttributeError:

            # Compatible with Shapely < 2.0
            ring = ring.buffer(0)

        # Skip empty geometries
        if ring.is_empty:
            continue

        rural_features.append(
            {
                "geometry": ring,
                "zone_id": int(row["zone_id"]),
                "zone_type": "rural",
            }
        )

# ============================================================
# Create GeoDataFrame
# ============================================================

    gdf_rural = gpd.GeoDataFrame(
        rural_features,
        crs=METRIC_CRS,
    )

    # Reproject to WGS84
    gdf_rural = gdf_rural.to_crs("EPSG:4326")

# ============================================================
# Export GeoJSON
# ============================================================

    gdf_rural.to_file(
        output_file,
        driver="GeoJSON",
    )

# ============================================================
# Summary
# ============================================================

    print("Rural zones created successfully.")
    print(f"Output file : {output_file}")
    print(f"Rural zones : {len(gdf_rural)}")

except Exception as e:

    print(f"Processing failed: {e}")
