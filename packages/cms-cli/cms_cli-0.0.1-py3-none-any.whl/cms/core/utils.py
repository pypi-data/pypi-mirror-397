import json
import os
from typing import Optional, Tuple

import geopandas as gpd
from copernicusmarine import login as cms_login
from dotenv import load_dotenv
from shapely.geometry import shape
from shapely.wkt import loads as load_wkt


def check_envs() -> None:
    user, password = _get_user_and_password()
    if not user or not password:
        raise ValueError("CMS_USER or CMS_PASSWORD environment variables are not set.")


def login() -> bool:
    user, password = _get_user_and_password()
    return cms_login(username=user, password=password, force_overwrite=True)


def _get_user_and_password() -> Tuple[Optional[str], Optional[str]]:
    user = os.getenv("COPERNICUSMARINE_SERVICE_USERNAME")
    password = os.getenv("COPERNICUSMARINE_SERVICE_PASSWORD")
    if not user or not password:
        load_dotenv()
        user = os.getenv("CMS_USER")
        password = os.getenv("CMS_PASSWORD")
    return user, password


def get_bbox_from_aoi(aoi: str) -> Tuple[float, float, float, float]:
    """
    Get the bounding box from various input formats.

    Args:
        aoi: The input AOI, which can be:
             - Filepath of a shapefile or GeoJSON
             - WKT string
             - GeoJSON as a string

    Returns:
        A bounding box (minx, miny, maxx, maxy)
    """
    epsg_wgs84 = "EPSG:4326"

    try:
        gdf = _parse_aoi_to_geodataframe(aoi, epsg_wgs84)
        return tuple(gdf.total_bounds)  # type: ignore
    except Exception as e:
        raise ValueError(f"Error processing AOI: {e}")


def _parse_aoi_to_geodataframe(aoi: str, target_crs: str) -> gpd.GeoDataFrame:
    """Parse AOI string to GeoDataFrame in target CRS."""
    if aoi.endswith((".shp", ".geojson", ".json")):
        return _load_file_as_geodataframe(aoi, target_crs)
    elif aoi.strip().upper().startswith(("POLYGON", "MULTIPOLYGON")):
        return _load_wkt_as_geodataframe(aoi, target_crs)
    else:
        return _load_geojson_string_as_geodataframe(aoi, target_crs)


def _load_file_as_geodataframe(filepath: str, target_crs: str) -> gpd.GeoDataFrame:
    """Load shapefile or GeoJSON file as GeoDataFrame."""
    gdf = gpd.read_file(filepath)
    if gdf.crs is not None and gdf.crs != target_crs:
        gdf = gdf.to_crs(target_crs)
    return gdf


def _load_wkt_as_geodataframe(wkt: str, crs: str) -> gpd.GeoDataFrame:
    """Load WKT string as GeoDataFrame."""
    geometry = load_wkt(wkt)
    return gpd.GeoDataFrame(geometry=[geometry], crs=crs)


def _load_geojson_string_as_geodataframe(geojson_str: str, crs: str) -> gpd.GeoDataFrame:
    """Load GeoJSON string as GeoDataFrame."""
    try:
        geojson_data = json.loads(geojson_str)
        geometry = shape(geojson_data.get("geometry", geojson_data))
        return gpd.GeoDataFrame(geometry=[geometry], crs=crs)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid AOI format. Could not parse GeoJSON string: {e}")
