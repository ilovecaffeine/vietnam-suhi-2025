"""
urban_01.py

Convert the GHS-SMOD raster into a binary urban mask.

Output classes
--------------
0 : Non-urban
1 : Urban
255 : NoData
"""
import numpy as np
import rasterio

# ============================================================
# Input and output files
# ============================================================

input_raster = r"C:\Users\admin\Documents\Code_for_fun\HUI\data\GHS_SMOD_clipped_vn.tif"
output_raster = r"C:\Users\admin\Documents\Code_for_fun\HUI\data\GHS_SMOD_urban_01.tif"

# ============================================================
# Urban class definition
# ============================================================

URBAN_CLASSES = [22, 23, 30]

# ============================================================
# Convert GHS-SMOD classes to a binary urban mask
# ============================================================

print("Creating binary urban mask...")

with rasterio.open(input_raster) as src:

    smod = src.read(1)
    nodata = src.nodata

    # Initialize all pixels as non-urban (0)
    urban = np.zeros(smod.shape, dtype=np.uint8)

    # Assign urban pixels (1)
    urban[np.isin(smod, URBAN_CLASSES)] = 1

    # Preserve NoData pixels (255)
    if nodata is not None:
        urban[smod == nodata] = 255

    profile = src.profile.copy()
    profile.update(
        dtype=rasterio.uint8,
        count=1,
        nodata=255,
        compress="lzw",
    )

    with rasterio.open(output_raster, "w", **profile) as dst:
        dst.write(urban, 1)

# ============================================================
# Summary
# ============================================================

print("Binary urban mask created successfully.")
print(f"Output raster : {output_raster}")

print(f"Urban pixels      : {np.sum(urban == 1):,}")
print(f"Non-urban pixels  : {np.sum(urban == 0):,}")
print(f"NoData pixels     : {np.sum(urban == 255):,}")