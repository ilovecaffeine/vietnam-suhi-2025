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

python src/compute_suhi.py

python src/create_statistics.py

python src/create_lisa.py

## Citation

If you use this repository, data, or source code in your research or project, please cite it as follows:

> **Tran, T. L. (2025)**. *Surface Urban Heat Island (SUHI) Analysis in Vietnam 2025* [Source code and Data]. GitHub. [https://github.com/ilovecaffeine/vietnam-suhi-2025](https://github.com/ilovecaffeine/vietnam-suhi-2025)

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
