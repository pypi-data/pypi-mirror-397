from datetime import datetime
from typing import List, Union

import click

from cms.commands import cms_data
from cms.core.enums import MagDirParameterName

HELP_TEMPORAL_RESOLUTION = """\b
Temporal resampling is defined using the pandas/xarray frequency parameter:
    - 'H': Hourly (e.g., '3H' => every 3rd hour)
    - 'D': Daily
    - 'MS': Month-start (e.g. 01.01 – 31.01 => timestamp labeled as 01.01)
    - 'QS': Quarter-start
    - 'AS': Year-start
If not specified, the original temporal resolution is preserved.
"""

HELP_RESAMPLING = """\b
Temporal resampling utilizes methods provided by xarray:
    - 'nearest': Select the value closest to the target timestamp
    - 'mean': Compute the average value
    - 'median': Compute the median value
    - 'min': Find the minimum value
    - 'max': Find the maximum value
    - 'count': Count the number of non-NA/null values
If not specified, the 'nearest' method is used.
"""


def validate_date(ctx, param, value):
    if value is None:
        return None
    try:
        datetime.strptime(value, "%Y-%m-%d").date()
        return value
    except ValueError:
        raise click.BadParameter(f"{value} is not in the correct format, expected YYYY-MM-DD.")


def common_options_decorator(*options):
    """Decorator factory to apply multiple Click options to a function"""

    def decorator(func):
        for option in reversed(options):
            func = option(func)
        return func

    return decorator


common_cms_options = common_options_decorator(
    click.option("-id", "--dataset-id", required=True, type=str, help="CMS Dataset ID"),
    click.option("-o", "--output_dir", required=True, type=str, help="Output directory"),
    click.option("-a", "--aoi", required=True, type=str, help="AOI as ESRI Shapefile, GeoJSON or WKT"),
    click.option("-s", "--start-date", required=True, type=str, help="Start date YYYY-MM-DD", callback=validate_date),
    click.option("-e", "--end-date", required=False, type=str, help="End date YYYY-MM-DD", callback=validate_date),
    click.option(
        "-d", "--depth", required=False, type=float, help="Depth dimension (only the given depth is used).", default=1.0
    ),
)

temporal_resampling_options = common_options_decorator(
    click.option("-t", "--temporal-resolution", required=False, type=str, help=HELP_TEMPORAL_RESOLUTION),
    click.option("-r", "--resampling", required=False, default="nearest", type=str, help=HELP_RESAMPLING),
)


@click.command()
@common_cms_options
@click.option("-fn", "--file-name", required=False, type=Union[str, None], help="Output file name (.nc)", default=None)
@click.option("-p", "--parameter", multiple=True, required=True, type=str, help="Parameter name in Dataset.")
def download_netcdf(
    dataset_id: str,
    file_name: str,
    parameter: List[str],
    aoi: str,
    start_date: str,
    end_date: str = "",
    output_dir: str = "",
    depth: float = 1.0,
):
    try:
        cms_data.download_netcdf(
            dataset_id=dataset_id,
            file_name=file_name,
            parameter=parameter,
            aoi=aoi,
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir,
            depth=depth,
        )
    except Exception as e:
        click.echo(f"Dataset could not be downloaded:\n{e}")


@click.command()
@common_cms_options
@click.option("-p", "--parameter", required=True, type=str, help="Parameter name in Dataset")
@temporal_resampling_options
@click.option("-re", "--resolution", required=False, type=int, help="Interpolated resolution in meters", default=None)
def create_scalar_geotiffs(
    dataset_id, parameter, aoi, start_date, end_date, temporal_resolution, resampling, output_dir, depth, resolution
):
    cms_data.create_scalar_geotiffs(
        dataset_id=dataset_id,
        aoi=aoi,
        parameter=parameter,
        start_date=start_date,
        end_date=end_date,
        output_dir=output_dir,
        depth=depth,
        temporal_resolution=temporal_resolution,
        resampling=resampling,
        resolution=resolution,
    )


@click.command()
@common_cms_options
@click.option("-di", "--direction", required=True, type=str, help="Direction parameter name in Dataset")
@click.option("-ht", "--height", required=True, type=str, help=" Height parameter name in Dataset")
@temporal_resampling_options
@click.option("-re", "--resolution", required=False, type=int, help="Interpolated resolution in meters", default=None)
def create_wave_geotiffs(
    dataset_id: str,
    direction: str,
    height: str,
    aoi: str,
    start_date: str,
    end_date: str = "",
    output_dir: str = "",
    depth: float = 1.0,
    temporal_resolution: str = "",
    resampling: str = "",
    resolution: int = None,
):
    try:
        cms_data.create_mag_dir_geotiffs(
            dataset_id=dataset_id,
            parameter1=height,
            parameter2=direction,
            aoi=aoi,
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir,
            depth=depth,
            parameter_type=MagDirParameterName.WAVE,
            temporal_resolution=temporal_resolution,
            resampling=resampling,
            resolution=resolution,
        )
    except Exception as e:
        click.echo(f"GeoTIFFs could not be created:\n{e}")


@click.command()
@common_cms_options
@click.option("-ew", "--east-wind", required=True, type=str, help="Eastward wind parameter name in Dataset")
@click.option("-nw", "--north-wind", required=True, type=str, help="Northward wind parameter name in Dataset")
@temporal_resampling_options
@click.option("-re", "--resolution", required=False, type=int, help="Interpolated resolution in meters", default=None)
def create_wind_geotiffs(
    dataset_id: str,
    east_wind: str,
    north_wind: str,
    aoi: str,
    start_date: str,
    end_date: str = "",
    output_dir: str = "",
    depth: float = 1.0,
    temporal_resolution: str = "",
    resampling: str = "",
    resolution: int = None,
):
    try:
        cms_data.create_mag_dir_geotiffs(
            dataset_id=dataset_id,
            parameter1=east_wind,
            parameter2=north_wind,
            aoi=aoi,
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir,
            depth=depth,
            parameter_type=MagDirParameterName.WIND,
            temporal_resolution=temporal_resolution,
            resampling=resampling,
            resolution=resolution,
        )
    except Exception as e:
        click.echo(f"GeoTIFFs could not be created:\n{e}")


@click.command()
@common_cms_options
@click.option(
    "-ev", "--east-cur-vel", required=True, type=str, help="Eastward current velocity parameter name in dataset"
)
@click.option("-nv", "--north-cur-vel", required=True, type=str, help="Northward current velocity  name in dataset")
@temporal_resampling_options
@click.option("-re", "--resolution", required=False, type=int, help="Interpolated resolution in meters", default=None)
def create_current_geotiffs(
    dataset_id: str,
    east_cur_vel: str,
    north_cur_vel: str,
    aoi: str,
    start_date: str,
    end_date: str = "",
    output_dir: str = "",
    depth: float = 1.0,
    temporal_resolution: str = "",
    resampling: str = "",
    resolution: int = None,
):
    try:
        cms_data.create_mag_dir_geotiffs(
            dataset_id=dataset_id,
            parameter1=east_cur_vel,
            parameter2=north_cur_vel,
            aoi=aoi,
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir,
            depth=depth,
            parameter_type=MagDirParameterName.CURRENT,
            temporal_resolution=temporal_resolution,
            resampling=resampling,
            resolution=resolution,
        )
    except Exception as e:
        click.echo(f"GeoTIFFs could not be created:\n{e}")
