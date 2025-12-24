import os
from typing import Dict, List, Optional, Tuple, Type, Union

import click
import copernicusmarine
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import Affine, from_origin
from xarray import DataArray, Dataset, open_dataset

from cms.core.enums import MagDirParameterName, ResamplingMethod
from cms.core.interpolation import fetch_water_mask, process_interpolation
from cms.core.magdircalculator import CurrentCalculator, MagDirCalculator, WaveCalculator, WindCalculator
from cms.core.utils import get_bbox_from_aoi, login

NO_DATA_VALUE = -9999


def download_netcdf(
    dataset_id: str,
    aoi: str,
    start_date: str,
    file_name: Union[str, None] = None,
    parameter: Union[List[str], None] = None,
    end_date: str = "",
    output_dir: str = "",
    depth: float = 1.0,
) -> str:
    if not login():
        raise Exception("Login to Copernicus Marine Service failed!")
    click.echo("Login to Copernicus Marine Service successfully!")

    min_x, min_y, max_x, max_y = get_bbox_from_aoi(aoi)

    response_subset = copernicusmarine.subset(
        dataset_id=dataset_id,
        variables=parameter,
        start_datetime=start_date,
        end_datetime=end_date,
        minimum_longitude=min_x,
        maximum_longitude=max_x,
        minimum_latitude=min_y,
        maximum_latitude=max_y,
        output_directory=output_dir,
        disable_progress_bar=True,
        maximum_depth=depth,
        output_filename=file_name,
    )
    return str(response_subset.file_path)


def create_scalar_geotiffs(
    dataset_id: str,
    aoi: str,
    parameter: str,
    start_date: str,
    end_date: str = "",
    output_dir: str = "",
    depth: float = 1.0,
    temporal_resolution: Optional[str] = None,
    resampling: Optional[str] = None,
    resolution: Optional[int] = None,
) -> None:
    metadata = get_metadata_from_dataset_id(dataset_id)
    netcdf_file_path = download_netcdf(
        dataset_id=dataset_id,
        aoi=aoi,
        start_date=start_date,
        parameter=[parameter],
        end_date=end_date,
        output_dir=output_dir,
        depth=depth,
    )
    process_scalar_netcdf(
        netcdf_file_path,
        output_dir,
        parameter,
        depth,
        temporal_resolution,
        resampling,
        metadata,
        resolution,
        aoi,
    )


def create_mag_dir_geotiffs(
    dataset_id: str,
    aoi: str,
    parameter1: str,
    parameter2: str,
    parameter_type: MagDirParameterName,
    start_date: str,
    end_date: str = "",
    output_dir: str = "",
    depth: float = 1.0,
    temporal_resolution: Optional[str] = None,
    resampling: Optional[str] = None,
    resolution: Optional[int] = None,
) -> None:
    netcdf_file_path = download_netcdf(
        dataset_id=dataset_id,
        aoi=aoi,
        start_date=start_date,
        parameter=[parameter1, parameter2],
        end_date=end_date,
        output_dir=output_dir,
        depth=depth,
    )
    metadata = get_metadata_from_dataset_id(dataset_id)
    process_mag_dir_netcdf(
        netcdf_file_path,
        output_dir,
        parameter1,
        parameter2,
        parameter_type,
        depth,
        temporal_resolution,
        resampling,
        metadata,
        resolution,
        aoi,
    )


def process_scalar_netcdf(
    netcdf_file_path: str,
    output_dir: str,
    parameter: str,
    depth: float,
    temporal_resolution: Optional[str],
    resampling: str,
    metadata: str = "",
    resolution: Optional[int] = None,
    aoi: str = "",
) -> None:
    ds = open_dataset(netcdf_file_path)
    if temporal_resolution is not None:
        resampling_enum = ResamplingMethod.from_string(resampling)
        ds = apply_resampling(ds, temporal_resolution, resampling_enum)

    transform = _get_transform_from_dataset(ds)
    parameter_data = ds[parameter]
    lon_name, lat_name = _get_lon_lat_names(ds)
    water_mask_gdf = _fetch_water_mask_if_needed(resolution, aoi, output_dir)

    for timestamp in ds.time:
        data_array = _extract_scalar_data_for_timestamp(ds, parameter_data, timestamp, depth, lon_name, lat_name)
        data_array, current_transform = _apply_interpolation_if_needed(
            data_array, ds, resolution, water_mask_gdf, lon_name, lat_name, transform
        )

        time_str = pd.to_datetime(timestamp.values).strftime("%Y%m%dT%H%M%S")
        output_file = os.path.join(output_dir, f"{parameter.upper()}_{time_str}.tif")
        create_geotiff(data_array, output_file, current_transform, metadata_abstract=metadata)
    ds.close()


def process_mag_dir_netcdf(
    netcdf_file_path: str,
    output_dir: str,
    parameter1: str,
    parameter2: str,
    parameter_type: MagDirParameterName,
    depth: float,
    temporal_resolution: Optional[str],
    resampling: str,
    metadata: str = "",
    resolution: Optional[int] = None,
    aoi: str = "",
) -> None:
    ds = open_dataset(netcdf_file_path)
    if temporal_resolution is not None:
        resampling_enum = ResamplingMethod.from_string(resampling)
        ds = apply_resampling(ds, temporal_resolution, resampling_enum)

    transform = _get_transform_from_dataset(ds)
    magnitude, direction = _calculate_magnitude_and_direction(ds, parameter1, parameter2, parameter_type)
    lon_name, lat_name = _get_lon_lat_names(ds)
    water_mask_gdf = _fetch_water_mask_if_needed(resolution, aoi, output_dir)

    for timestamp in ds.time:
        data_array = _extract_mag_dir_data_for_timestamp(
            ds, magnitude, direction, timestamp, depth, lon_name, lat_name
        )
        data_array, current_transform = _apply_interpolation_if_needed(
            data_array, ds, resolution, water_mask_gdf, lon_name, lat_name, transform
        )

        time_str = pd.to_datetime(timestamp.values).strftime("%Y%m%dT%H%M%S")
        output_file = os.path.join(output_dir, f"{parameter_type.value.upper()[:3]}_{time_str}.tif")
        create_geotiff(data_array, output_file, current_transform, metadata_abstract=metadata)
    ds.close()


def create_geotiff(
    data: np.ndarray,
    output_file: str,
    transform: Union[Affine, Tuple],
    nodata_value: float = NO_DATA_VALUE,
    metadata_abstract: str = "",
) -> None:
    if data.ndim != 3:
        raise ValueError("Input data must have 3 dimensions (bands, height, width).")
    nb_bands = data.shape[0]
    height, width = data.shape[-2:]
    if os.path.exists(output_file):
        click.echo(f"Output file {output_file} already exists. Skipping.")
        return
    with rasterio.open(
        output_file,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=nb_bands,
        dtype=data.dtype,
        crs="EPSG:4326",
        transform=transform,
        nodata=nodata_value,
    ) as dst:
        if metadata_abstract:
            dst.update_tags(EOMAP_ABSTRACT=metadata_abstract)
        dst.write(data)


def apply_resampling(ds: Dataset, time_frequency: str, method: ResamplingMethod) -> Dataset:
    resampler = ds.resample(time=time_frequency)
    resample_func = getattr(resampler, method.value)
    return resample_func()


def get_metadata_from_dataset_id(dataset_id: str) -> str:
    base_text = "Generated using E.U. Copernicus Marine Service Information"
    cm_catalogue = copernicusmarine.describe(dataset_id=dataset_id, disable_progress_bar=True)

    if not cm_catalogue or not hasattr(cm_catalogue, "products") or not cm_catalogue.products:
        warning_message = f"Warning: Dataset {dataset_id} not found or has no products."
        click.secho(warning_message, err=True)
        return f"{base_text}; {dataset_id}"

    product = cm_catalogue.products[0]
    doi = getattr(product, "digital_object_identifier", None)
    if not doi:
        warning_message = f"Warning: Cannot extract DOI from Copernicus Marine Catalogue for dataset {dataset_id}!"
        click.secho(warning_message, err=True)
        return f"{base_text}; {dataset_id}"

    return f"{base_text}; https://doi.org/{doi}"


def _fetch_water_mask_if_needed(
    resolution: Optional[int], aoi: str, output_dir: str
) -> Optional[gpd.GeoDataFrame]:
    """Fetch water mask if interpolation is requested."""
    if resolution is None:
        return None
    bbox = get_bbox_from_aoi(aoi)
    water_mask_gdf = fetch_water_mask(bbox, cache_dir=output_dir)
    click.echo(f"Water mask fetched for AOI with {len(water_mask_gdf)} polygon(s)")
    return water_mask_gdf


def _extract_scalar_data_for_timestamp(
    ds: Dataset, parameter_data: DataArray, timestamp: DataArray, depth: float, lon_name: str, lat_name: str
) -> np.ndarray:
    """Extract scalar data array for a single timestamp."""
    select_conditions = {"time": timestamp, "depth": depth} if "depth" in ds else {"time": timestamp}
    data_array = np.ndarray((1, ds[lat_name].size, ds[lon_name].size), dtype=np.float32)
    data_array[0, :, :] = np.flip(parameter_data.sel(select_conditions, method="nearest").values, axis=0)
    data_array[np.isnan(data_array)] = NO_DATA_VALUE
    return data_array


def _extract_mag_dir_data_for_timestamp(
    ds: Dataset,
    magnitude: Union[DataArray, np.ndarray],
    direction: Union[DataArray, np.ndarray],
    timestamp: DataArray,
    depth: float,
    lon_name: str,
    lat_name: str,
) -> np.ndarray:
    """Extract magnitude and direction data arrays for a single timestamp."""
    select_conditions = {"time": timestamp, "depth": depth} if "depth" in ds else {"time": timestamp}
    data_array = np.ndarray((2, ds[lat_name].size, ds[lon_name].size), dtype=np.float32)
    data_array[0, :, :] = np.flip(magnitude.sel(select_conditions, method="nearest").values, axis=0)
    data_array[1, :, :] = np.flip(direction.sel(select_conditions, method="nearest").values, axis=0)
    data_array[np.isnan(data_array)] = NO_DATA_VALUE
    return data_array


def _calculate_bounds_from_dataset(ds: Dataset, lon_name: str, lat_name: str) -> rasterio.coords.BoundingBox:
    """Calculate pixel-extent bounds from dataset including half-pixel buffer."""
    lon = ds[lon_name]
    lat = ds[lat_name]
    x_res = (lon[1] - lon[0]).item()
    y_res = (lat[1] - lat[0]).item()
    return rasterio.coords.BoundingBox(
        left=lon.min().item() - 0.5 * x_res,
        bottom=lat.min().item() - 0.5 * abs(y_res),
        right=lon.max().item() + 0.5 * x_res,
        top=lat.max().item() + 0.5 * abs(y_res),
    )


def _apply_interpolation_if_needed(
    data_array: np.ndarray,
    ds: Dataset,
    resolution: Optional[int],
    water_mask_gdf: Optional[gpd.GeoDataFrame],
    lon_name: str,
    lat_name: str,
    default_transform: Union[Affine, Tuple],
) -> Tuple[np.ndarray, Union[Affine, Tuple]]:
    """Apply interpolation to data array if requested and return updated data and transform."""
    if resolution is None:
        return data_array, default_transform

    bounds = _calculate_bounds_from_dataset(ds, lon_name, lat_name)
    interpolated_data, new_transform = process_interpolation(
        data_array, bounds, resolution, water_mask_gdf, NO_DATA_VALUE, interpolate_missing=True
    )
    return interpolated_data, new_transform


def _calculate_magnitude_and_direction(
    ds: Dataset, parameter1: str, parameter2: str, parameter_type: MagDirParameterName
) -> Tuple[Union[DataArray, np.ndarray], Union[DataArray, np.ndarray]]:
    """Calculate magnitude and direction from two parameters."""
    calculator_class = _get_mag_dir_calculator(parameter_type)
    calculator = calculator_class(ds[parameter1], ds[parameter2])
    return calculator.get_mag(), calculator.get_dir()


def _get_mag_dir_calculator(parameter_type: MagDirParameterName) -> Type[MagDirCalculator]:
    calculators: Dict[MagDirParameterName, Type[MagDirCalculator]] = {
        MagDirParameterName.WAVE: WaveCalculator,
        MagDirParameterName.CURRENT: CurrentCalculator,
        MagDirParameterName.WIND: WindCalculator,
    }
    return calculators.get(parameter_type, MagDirCalculator)


def _get_transform_from_dataset(ds: Dataset) -> Affine:
    lon_name, lat_name = _get_lon_lat_names(ds)
    lon = ds[lon_name]
    lat = ds[lat_name]
    x_res = (lon[1] - lon[0]).item()
    y_res = (lat[1] - lat[0]).item()
    # CMS follows Climate and Forecast (CF) Metadata Conventions:
    # https://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/cf-conventions.html#coordinate-types
    # Lon/Lat should be middle of grid cell, for GeoTIFF we need the upper left corner
    return from_origin(lon.min().item() - 0.5 * x_res, lat.max().item() + 0.5 * y_res, x_res, y_res)


def _get_lon_lat_names(ds: Dataset) -> Tuple[str, str]:
    def get_name(names: Tuple[str, ...]) -> str:
        for name in names:
            if name in ds.dims:
                return name
        return ""

    lon_name = get_name(("longitude", "lon"))
    lat_name = get_name(("latitude", "lat"))
    if not lon_name or not lat_name:
        raise ValueError("No possible lon or lat names found.")
    return lon_name, lat_name
