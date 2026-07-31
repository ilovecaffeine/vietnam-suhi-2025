"""
rural_01.py

Convert the GHS-SMOD raster into a binary rural mask.

Output classes
--------------
0 : Non-rural
1 : Rural
255 : NoData
"""

from pathlib import Path

import numpy as np
import rasterio

# ============================================================
# Project directories
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"

# ============================================================
# Input and output files
# ============================================================

input_raster = RAW_DIR / "GHS_SMOD_clipped_vn.tif"

output_raster = INTERMEDIATE_DIR / "GHS_SMOD_rural_01.tif"

# ============================================================
# Rural class definition
# ============================================================

RURAL_CLASSES = [11, 12, 13]

# ============================================================
# Convert GHS-SMOD classes to a binary rural mask
# ============================================================

print("Creating binary rural mask...")

with rasterio.open(input_raster) as src:

    smod = src.read(1)
    nodata = src.nodata

    # Initialize all pixels as non-rural (0)
    rural = np.zeros(smod.shape, dtype=np.uint8)

    # Assign rural pixels (1)
    rural[np.isin(smod, RURAL_CLASSES)] = 1

    # Preserve NoData pixels (255)
    if nodata is not None:
        rural[smod == nodata] = 255

    profile = src.profile.copy()
    profile.update(
        dtype=rasterio.uint8,
        count=1,
        nodata=255,
        compress="lzw",
    )

    with rasterio.open(output_raster, "w", **profile) as dst:
        dst.write(rural, 1)

# ============================================================
# Summary
# ============================================================

print("Binary rural mask created successfully.")
print(f"Output raster : {output_raster}")

print(f"Rural pixels      : {np.sum(rural == 1):,}")
print(f"Non-rural pixels  : {np.sum(rural == 0):,}")
print(f"NoData pixels     : {np.sum(rural == 255):,}")