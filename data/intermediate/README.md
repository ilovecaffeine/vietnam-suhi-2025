# Intermediate Data

This directory contains intermediate datasets generated during preprocessing and spatial analysis.

These files are created automatically by the processing scripts in `src/` and can be regenerated at any time.

---

## Files

### `GHS_SMOD_rural_01.tif`
Binary raster representing rural areas extracted from the GHS-SMOD dataset.

### `GHS_SMOD_urban_01.tif`
Binary raster representing urban areas extracted from the GHS-SMOD dataset.

### `GHS_SMOD_urban_01_filtered.tif`
Filtered urban binary raster after removing small urban clusters below the minimum mapping area threshold.

### `GHS_SMOD_urban_id.tif`
Raster in which each urban cluster is assigned a unique identifier.

### `urban_zones.geojson`
Vector polygons representing individual urban clusters with geometric attributes.

### `rural_zones.geojson`
Vector polygons representing rural reference zones (ring buffers) associated with each urban cluster for SUHI estimation.
