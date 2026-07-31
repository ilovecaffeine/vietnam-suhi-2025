# Raw Data

This directory stores the original input datasets used for calculating the Surface Urban Heat Island (SUHI) index in Vietnam for 2025.

---

## 📁 Directory Structure & Files

### 📂 Subdirectories
* **`GHS-SMOD/`**: Contains raw Global Human Settlement Layer (GHS-SMOD) datasets used for urban and rural area classification.
* **`HUMDATA/`**: Contains Vietnam administrative boundary spatial data downloaded from HDX.
* **`MYD11A2/`**: Contains MODIS Aqua Land Surface Temperature (LST) 8-day 1km datasets and the Google Earth Engine (GEE) export script.

### 📄 Clipped GeoTIFF Files
* **`GHS_SMOD_clipped_vn.tif`**: Urban/rural settlement classification raster clipped to Vietnam's national boundary.
* **`MYD11A2_A2025_clipped_vn.tif`**: Median Land Surface Temperature (LST) 2025 raster clipped to Vietnam's national boundary.

