# Surface Urban Heat Island (SUHI) Analysis in Vietnam 2025
A Python workflow for estimating and analyzing Surface Urban Heat Island (SUHI) intensity.

## Overview

This repository provides a reproducible workflow for estimating and analyzing Surface Urban Heat Island (SUHI) intensity across urban areas in Vietnam during the April–August 2025 study period using MODIS MYD11A2 Land Surface Temperature (LST) and GHS-SMOD urban extent datasets.

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
.
├── 📁 src/                   # Python source code
├── 📁 data/                  # Data directory
│   ├── 📁 raw/               # Raw input datasets
│   ├── 📁 intermediate/      # Intermediate processing outputs
│   └── 📁 results/           # Final datasets and Excel reports
├── 📁 figures/               # Generated figures and visual plots
└── 📁 docs/                  # Project documentation
```

## Data

The analysis uses the following publicly available datasets:

### 1. MODIS Land Surface Temperature (MYD11A2)
> **Wan, Z., Hook, S., & Hulley, G. (2021)**. *MODIS/Aqua Land Surface Temperature/Emissivity 8-Day L3 Global 1km SIN Grid V061* [Dataset]. NASA Land Processes Distributed Active Archive Center. [https://doi.org/10.5067/MODIS/MYD11A2.061](https://doi.org/10.5067/MODIS/MYD11A2.061) *(Accessed: 2026-07-17)*

### 2. Global Human Settlement Layer (GHS-SMOD)
> **Schiavina, M., Melchiorri, M., & Pesaresi, M. (2023)**. *GHS-SMOD R2023A - GHS settlement layers, application of the Degree of Urbanisation methodology (stage I) to GHS-POP R2023A and GHS-BUILT-S R2023A, multitemporal (1975-2030)*. European Commission, Joint Research Centre (JRC).<br>
> 🔗 **PID:** [http://data.europa.eu/89h/a0df7a6f-49de-46ea-9bde-563437a6e2ba](http://data.europa.eu/89h/a0df7a6f-49de-46ea-9bde-563437a6e2ba)<br>
> 🔗 **DOI:** [10.2905/A0DF7A6F-49DE-46EA-9BDE-563437A6E2BA](https://doi.org/10.2905/A0DF7A6F-49DE-46EA-9BDE-563437A6E2BA)

### 3. Viet Nam Administrative Boundaries (UN OCHA)
> **UN OCHA (2025)**. *Viet Nam - Subnational Administrative Boundaries* [Dataset]. Humanitarian Data Exchange (HDX). [https://data.humdata.org/dataset/cod-ab-vnm](https://data.humdata.org/dataset/cod-ab-vnm) *(Accessed: 2026-07-17)*

Please cite the original data providers when using these datasets.

## Installation

### Requirements

- Python 3.11 or later

### Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

Run the processing scripts in the following order:

```bash
python src/urban_01.py
python src/rural_01.py
python src/urban_01_filter.py
python src/urban_zone_polygonize.py
python src/rural_zone_buffer.py
python src/calSUHI.py
python src/create_statistics.py
```

The workflow performs the following steps:

1. Extract urban areas from the GHS-SMOD dataset.
2. Extract rural areas from the GHS-SMOD dataset.
3. Remove small urban clusters and assign unique IDs.
4. Convert urban clusters into vector polygons.
5. Generate rural reference zones using 2–10 km ring buffers.
6. Calculate Surface Urban Heat Island (SUHI) intensity for each urban zone.
7. Generate summary statistics, spatial autocorrelation analysis, and figures.

Final outputs are saved in:

- `data/results/`
- `figures/`

## Citation

If you use this repository, data, or source code in your research or project, please cite it as follows:

> **Tran, T. L. (2025)**. *Surface Urban Heat Island (SUHI) Analysis in Vietnam 2025*. GitHub. [https://github.com/ilovecaffeine/vietnam-suhi-2025](https://github.com/ilovecaffeine/vietnam-suhi-2025)

### BibTeX

```bibtex
@misc{tran2025vietnam_suhi,
  author       = {Tran, Thien Loc},
  title        = {Surface Urban Heat Island (SUHI) Analysis in Vietnam 2025},
  year         = {2025},
  publisher    = {GitHub},
  journal      = {GitHub repository},
  howpublished = {\url{https://github.com/ilovecaffeine/vietnam-suhi-2025}}
}
