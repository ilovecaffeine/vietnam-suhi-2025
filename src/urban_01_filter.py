"""
urban_01_filter.py

Filter urban clusters by a minimum area threshold and assign
a unique identifier to each remaining urban zone.

Outputs
-------
- Binary urban mask after filtering
- Urban ID raster
- Urban zone attribute table
"""

import numpy as np
import pandas as pd
import rasterio
from pathlib import Path
from skimage.measure import label

# ============================================================
# Project directories
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"
RESULT_DIR = DATA_DIR / "results"

# ============================================================
# Input and output files
# ============================================================

input_raster = INTERMEDIATE_DIR / "GHS_SMOD_urban_01.tif"

output_binary = INTERMEDIATE_DIR / "GHS_SMOD_urban_01_filtered.tif"

output_id = INTERMEDIATE_DIR / "GHS_SMOD_urban_id.tif"

output_table = RESULT_DIR / "urban_id_table.csv"

# ============================================================
# Processing parameters
# ============================================================

MIN_AREA_KM2 = 10.0

# ============================================================
# Read input raster
# ============================================================

print("Filtering urban clusters...")

with rasterio.open(input_raster) as src:

    urban = src.read(1)
    profile = src.profile.copy()
    nodata = src.nodata

    # Create binary urban mask
    urban_mask = urban == 1

    # Label connected components (8-neighbor connectivity)
    labels = label(
        urban_mask,
        connectivity=2,
    )

    # Compute pixel area (km²)
    pixel_width = abs(src.transform.a)
    pixel_height = abs(src.transform.e)

    pixel_area_km2 = (
        pixel_width * pixel_height
    ) / 1_000_000

    # Count pixels for each connected component
    counts = np.bincount(labels.ravel())

    # Compute component area (km²)
    areas = counts * pixel_area_km2

    # Select components above the minimum area threshold
    valid_ids = np.where(areas >= MIN_AREA_KM2)[0]

    # Remove background label
    valid_ids = valid_ids[valid_ids != 0]

    # ========================================================
    # Assign sequential urban IDs
    # ========================================================

    urban_id = np.zeros(
        labels.shape,
        dtype=np.uint32,
    )

    mapping = []

    new_id = 1

    for old_id in valid_ids:

        urban_id[labels == old_id] = new_id

        mapping.append(
            {
                "urban_id": new_id,
                "old_label": int(old_id),
                "pixel_count": int(counts[old_id]),
                "area_km2": float(areas[old_id]),
            }
        )

        new_id += 1

    # ========================================================
    # Create filtered binary mask
    # ========================================================

    binary = np.zeros(
        labels.shape,
        dtype=np.uint8,
    )

    binary[urban_id > 0] = 1

    # Preserve NoData pixels
    if nodata is not None:

        binary[urban == nodata] = 255

        urban_id[urban == nodata] = 65535

# ============================================================
# Save filtered binary raster
# ============================================================

profile_bin = profile.copy()

profile_bin.update(
    dtype=rasterio.uint8,
    nodata=255,
    compress="lzw",
)

with rasterio.open(
    output_binary,
    "w",
    **profile_bin,
) as dst:

    dst.write(binary, 1)

# ============================================================
# Save urban ID raster
# ============================================================

profile_id = profile.copy()

profile_id.update(
    dtype=rasterio.uint16,
    nodata=65535,
    compress="lzw",
)

with rasterio.open(
    output_id,
    "w",
    **profile_id,
) as dst:

    dst.write(
        urban_id.astype(np.uint16),
        1,
    )

# ============================================================
# Save urban attribute table
# ============================================================

urban_table = pd.DataFrame(mapping)

urban_table.to_csv(
    output_table,
    index=False,
)

# ============================================================
# Summary
# ============================================================

print("Urban cluster filtering completed successfully.")
print(f"Minimum area threshold : {MIN_AREA_KM2:.2f} km²")
print(f"Pixel area             : {pixel_area_km2:.6f} km²")
print(f"Total clusters         : {len(counts) - 1}")
print(f"Retained clusters      : {len(valid_ids)}")
print(f"Removed clusters       : {len(counts) - 1 - len(valid_ids)}")

print()
print(f"Filtered binary mask : {output_binary}")
print(f"Urban ID raster      : {output_id}")
print(f"Urban attribute table: {output_table}")