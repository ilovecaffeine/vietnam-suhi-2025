# Surface Urban Heat Island (SUHI) Analysis in Vietnam 2025
A Python workflow for estimating and analyzing Surface Urban Heat Island (SUHI) intensity.

## Overview

This repository provides a reproducible workflow for estimating and analyzing Surface Urban Heat Island (SUHI) intensity across urban areas in Vietnam using remotely sensed land surface temperature and urban extent datasets.

## Features

- Urban zone extraction
- Estimate urban and rural land surface temperature
- Calculate Surface Urban Heat Island (SUHI) intensity
- Generate descriptive statistics
- Bootstrap confidence intervals
- Global Moran's I
- Local Moran's I (LISA)
- Urban–rural thermal contribution analysis

## Repository Structure

```text
src/                 Python source code
data/
    raw/             Raw input datasets (not included)
    intermediate/    Intermediate processing outputs
    results/         Final datasets and Excel reports
figures/             Generated figures
docs/                Project documentation
```

## Data

The analysis uses the following publicly available datasets:

- **MODIS Land Surface Temperature (LST)** – NASA MODIS Collection 6.1
- **GHS-SMOD** – Global Human Settlement Layer (European Commission)

The raw datasets are not distributed with this repository. Please download them from their official sources before running the workflow.

## Installation
Python 3.11

geopandas

numpy

pandas

matplotlib

esda

libpysal

pip install -r requirements.txt

## Usage

python src/compute_suhi.py

python src/create_statistics.py

python src/create_lisa.py

## Citation

If you use this repository, please cite:
...
