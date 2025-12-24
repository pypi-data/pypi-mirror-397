"""Spatial interpolation module for increasing GeoTIFF resolution with water mask."""

import os
from typing import Optional, Tuple

import geopandas as gpd
import numpy as np
import rasterio
from rasterio import features
from rasterio.transform import from_bounds
from scipy.interpolate import RegularGridInterpolator, griddata

WATER_POLYGON_URL = "https://public-geodata.s3.eu-central-1.amazonaws.com/water_mask/water_polygons.fgb"


def fetch_water_mask(bbox: Tuple[float, float, float, float], cache_dir: Optional[str] = None) -> gpd.GeoDataFrame:
    """
    Fetch water polygon mask from remote source and cache it.

    Args:
        bbox: Bounding box as (min_x, min_y, max_x, max_y) in EPSG:4326
        cache_dir: Optional directory to cache the water mask file

    Returns:
        GeoDataFrame containing unified water polygons in EPSG:4326
    """
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, "water_mask_cache.fgb")
        if os.path.exists(cache_path):
            gdf = gpd.read_file(cache_path, bbox=bbox)
        else:
            gdf = gpd.read_file(WATER_POLYGON_URL, bbox=bbox)
            gdf.to_file(cache_path, driver="FlatGeobuf")
    else:
        gdf = gpd.read_file(WATER_POLYGON_URL, bbox=bbox)

    if gdf.empty:
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")

    unified = gdf.union_all()
    return gpd.GeoDataFrame(geometry=[unified], crs=gdf.crs)


def interpolate_missing_values(data: np.ndarray, method: str = "cubic") -> np.ndarray:
    """
    Interpolate missing/NaN values in a 2D array using scipy griddata.

    Interpolates with the specified method (cubic/linear), then fills remaining NaN values
    (outside the convex hull) with nearest neighbor extrapolation.

    Args:
        data: 2D numpy array with potential NaN values
        method: Interpolation method ('linear', 'cubic', 'nearest')

    Returns:
        2D numpy array with interpolated and extrapolated values
    """
    if data.ndim != 2:
        raise ValueError("Input data must be 2D")

    rows, cols = data.shape
    row_coords, col_coords = np.meshgrid(np.arange(rows), np.arange(cols), indexing="ij")

    valid_mask = ~np.isnan(data)

    if not valid_mask.any():
        return data

    valid_points = np.column_stack([row_coords[valid_mask], col_coords[valid_mask]])
    valid_values = data[valid_mask]

    if valid_mask.all():
        return data

    all_points = np.column_stack([row_coords.ravel(), col_coords.ravel()])

    interpolated = griddata(valid_points, valid_values, all_points, method=method)

    outside_interpolation_mask = np.isnan(interpolated)
    if outside_interpolation_mask.any():
        nearest_values = griddata(valid_points, valid_values, all_points, method="nearest")
        interpolated[outside_interpolation_mask] = nearest_values[outside_interpolation_mask]

    return interpolated.reshape(data.shape)


def meters_to_degrees(meters: float, latitude: float) -> Tuple[float, float]:
    """
    Convert meters to degrees, accounting for latitude distortion.

    Args:
        meters: Target resolution in meters
        latitude: Center latitude of the area (for longitude correction)

    Returns:
        Tuple of (degrees_lon, degrees_lat)
    """
    degrees_lat = meters / 111320
    degrees_lon = meters / (111320 * np.cos(np.radians(latitude)))
    return degrees_lon, degrees_lat


def increase_resolution(
        data: np.ndarray,
        bounds: rasterio.coords.BoundingBox,
        target_resolution_meters: float,
        method: str = "linear",
) -> Tuple[np.ndarray, rasterio.transform.Affine]:
    """
    Increase resolution of raster data, with target resolution in meters.
    Works for WGS84 (EPSG:4326) input - output remains in same CRS.
    Preserves the exact extent of the input raster.

    Args:
        data: Input array of shape (bands, height, width)
        bounds: Bounding box in the raster's CRS (e.g., EPSG:4326)
        target_resolution_meters: Target resolution in meters
        method: Interpolation method ('linear', 'cubic', 'nearest')

    Returns:
        Tuple of (interpolated_data, new_transform)
    """
    if data.ndim != 3:
        raise ValueError("Input data must have 3 dimensions (bands, height, width)")

    nb_bands, rows, cols = data.shape

    center_lat = (bounds.bottom + bounds.top) / 2.0
    target_res_lon, target_res_lat = meters_to_degrees(target_resolution_meters, center_lat)

    target_res_lon = abs(float(target_res_lon))
    target_res_lat = abs(float(target_res_lat))
    if target_res_lon == 0.0 or target_res_lat == 0.0:
        raise ValueError("Target resolution converted to degrees is zero; check inputs.")

    extent_lon = bounds.right - bounds.left
    extent_lat = bounds.top - bounds.bottom

    new_width = max(1, int(np.round(extent_lon / target_res_lon)))
    new_height = max(1, int(np.round(extent_lat / target_res_lat)))

    if new_width == 0 or new_height == 0:
        raise ValueError("Computed target shape is zero; resolution may be too coarse for the bounds.")

    interpolated_data = np.empty((nb_bands, new_height, new_width), dtype=np.float64)

    y = np.arange(rows, dtype=np.float64)
    x = np.arange(cols, dtype=np.float64)

    y_new = np.linspace(0.0, rows - 1.0, new_height, dtype=np.float64)
    x_new = np.linspace(0.0, cols - 1.0, new_width, dtype=np.float64)

    xx, yy = np.meshgrid(x_new, y_new)
    points = np.column_stack([yy.ravel(), xx.ravel()])

    for band_idx in range(nb_bands):
        band = data[band_idx].astype(np.float64)

        interpolator = RegularGridInterpolator(
            (y, x),
            band,
            method=method,
            bounds_error=False,
            fill_value=np.nan,
        )

        interpolated_data[band_idx] = interpolator(points).reshape(new_height, new_width)

    new_transform = from_bounds(
        bounds.left, bounds.bottom, bounds.right, bounds.top,
        new_width, new_height
    )

    return interpolated_data, new_transform


def apply_water_mask(
        data: np.ndarray, transform: rasterio.transform.Affine, water_mask_gdf: gpd.GeoDataFrame, nodata_value: float
) -> np.ndarray:
    """
    Apply water mask to raster data, setting non-water areas to nodata.

    Args:
        data: Input array of shape (bands, height, width)
        transform: Rasterio affine transform
        water_mask_gdf: GeoDataFrame with water polygons in EPSG:4326
        nodata_value: Value to use for masked (non-water) pixels

    Returns:
        Masked array with non-water areas set to nodata
    """
    if data.ndim != 3:
        raise ValueError("Input data must have 3 dimensions (bands, height, width)")

    nb_bands, height, width = data.shape

    if water_mask_gdf.empty or len(water_mask_gdf) == 0:
        return np.full_like(data, nodata_value)

    shapes = [(geom, 1) for geom in water_mask_gdf.geometry if geom is not None]

    if not shapes:
        return np.full_like(data, nodata_value)

    water_raster = features.rasterize(
        shapes=shapes, out_shape=(height, width), transform=transform, fill=0, dtype=np.uint8
    )

    masked_data = data.copy()
    for band_idx in range(nb_bands):
        masked_data[band_idx][water_raster == 0] = nodata_value

    return masked_data


def process_interpolation(
        data: np.ndarray,
        bounds: rasterio.coords.BoundingBox,
        target_resolution_meters: float,
        water_mask_gdf: Optional[gpd.GeoDataFrame] = None,
        nodata_value: float = -9999,
        interpolate_missing: bool = True,
) -> Tuple[np.ndarray, rasterio.transform.Affine]:
    """
    Complete interpolation pipeline: interpolate missing values, increase resolution, apply water mask.

    Args:
        data: Input array of shape (bands, height, width)
        bounds: Bounding box in EPSG:4326
        target_resolution_meters: Target resolution in meters
        water_mask_gdf: Optional GeoDataFrame with water polygons
        nodata_value: Value representing nodata
        interpolate_missing: Whether to interpolate missing values first

    Returns:
        Tuple of (processed_data, new_transform)
    """
    if data.ndim != 3:
        raise ValueError("Input data must have 3 dimensions (bands, height, width)")

    nb_bands = data.shape[0]

    if interpolate_missing:
        for band_idx in range(nb_bands):
            band_data = data[band_idx].copy()
            band_data[band_data == nodata_value] = np.nan

            if not np.all(np.isnan(band_data)):
                try:
                    interpolated_band = interpolate_missing_values(band_data, method="cubic")
                    data[band_idx] = interpolated_band
                except Exception:
                    try:
                        interpolated_band = interpolate_missing_values(band_data, method="linear")
                        data[band_idx] = interpolated_band
                    except Exception:
                        pass

    interpolated_data, new_transform = increase_resolution(data, bounds, target_resolution_meters, method="linear")

    if water_mask_gdf is not None and not water_mask_gdf.empty:
        interpolated_data = apply_water_mask(interpolated_data, new_transform, water_mask_gdf, nodata_value)
    else:
        interpolated_data[np.isnan(interpolated_data)] = nodata_value

    return interpolated_data, new_transform
