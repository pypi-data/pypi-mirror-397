Copernicus Marine Service - CLI
=================

A command-line tool for downloading and converting Copernicus Marine Service datasets to GeoTIFF format. This tool simplifies access to oceanographic data including currents, waves, wind, and scalar parameters.

[![PyPI version](https://badge.fury.io/py/cms-cli.svg)](https://badge.fury.io/py/cms-cli)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

## Table of Content

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Commands Overview](#commands-overview)
- [Examples](#examples)
- [Development](#development)
- [License](#license)

## Features

- Download Copernicus Marine Service datasets in NetCDF format
- Convert ocean parameters to GeoTIFF format with spatial interpolation
- Generate specialized GeoTIFFs for:
  - Ocean currents (speed and direction)
  - Wave parameters (height and direction)
  - Wind data (speed and direction)
  - Scalar parameters (temperature, salinity, etc.)
- Configurable spatial resolution and bounding boxes
- Command-line interface for automation and scripting

## Installation

**Requires:** Python >=3.12

### End User Installation

Install via pip:

```bash
pip install cms-cli
```

Or using [uv](https://github.com/astral-sh/uv) (recommended):

```bash
uv pip install cms-cli
```

### Configuration

Before using the CLI, you need to configure your Copernicus Marine Service credentials.

#### Usage as library

Create a `.env` file in the root directory of your project with the following content:
```.dotenv
CMS_USER
CMS_PASSWORD
```

Or set them as environment variables:

```bash
export CMS_USER="your_username"
export CMS_PASSWORD="your_password"
```

#### Development Installation

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   nano .env  # Or use any text editor
   ```

You can obtain credentials by registering at the [Copernicus Marine Service](https://marine.copernicus.eu/).

## Usage

After installation, run the CLI using:

```bash
cms-cli --help
```

### Development Installation

For contributing or development:

```bash
git clone https://github.com/EomapCompany/cms-cli
cd cms-cli

# Install with all development dependencies
uv sync --all-groups
```

Run tests:

```bash
uv run pytest tests/ -v
```

## Commands Overview

| Command                 | Description                                                                                          |
|-------------------------|------------------------------------------------------------------------------------------------------|
| `download-netcdf`       | Download original dataset with multiple parameters in NetCDF format                                  |
| `create-scalar-geotiffs`| Download dataset and create GeoTIFFs for scalar parameters (e.g., temperature, salinity)             |
| `create-current-geotiffs`| Download dataset and create current GeoTIFFs (speed and direction)                                  |
| `create-wave-geotiffs`  | Download dataset and create wave GeoTIFFs (height and direction)                                     |
| `create-wind-geotiffs`  | Download dataset and create wind GeoTIFFs (speed and direction)                                      |

## Examples

### Download NetCDF data

```bash
cms-cli download-netcdf \
  --dataset-id cmems_mod_glo_phy_my_0.083deg_P1D-m \
  --variables thetao \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --output-dir ./data
```

### Create scalar GeoTIFFs

```bash
cms-cli create-scalar-geotiffs \
  --dataset-id cmems_mod_glo_phy_my_0.083deg_P1D-m \
  --variable thetao \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --resolution 1000 \
  --output-dir ./output
```

### Create current GeoTIFFs with bounding box

```bash
cms-cli create-current-geotiffs \
  --dataset-id cmems_mod_glo_phy_my_0.083deg_P1D-m \
  --u-variable uo \
  --v-variable vo \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --bbox -10 35 5 45 \
  --resolution 1000 \
  --output-dir ./currents
```

## Development

### Running Tests

```bash
uv run pytest tests/ -v
```

### Code Quality

This project uses `ruff` for linting and formatting:

```bash
uv run ruff check .
uv run ruff format .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0) - see the [LICENCE.md](LICENCE.md) file for details.

Copyright (c) 2025 EOMAP

## Acknowledgments

This tool uses the [Copernicus Marine Service](https://marine.copernicus.eu/) API to access ocean data.
