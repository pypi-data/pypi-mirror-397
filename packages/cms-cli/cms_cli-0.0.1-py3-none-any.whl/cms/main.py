import click

from cms.cli import cms_data
from cms.core.utils import check_envs


@click.group()
@click.version_option(package_name="cms-cli")
def cli():
    pass


cli.add_command(cms_data.download_netcdf)
cli.add_command(cms_data.create_scalar_geotiffs)
cli.add_command(cms_data.create_wave_geotiffs)
cli.add_command(cms_data.create_wind_geotiffs)
cli.add_command(cms_data.create_current_geotiffs)


def main():
    check_envs()
    cli()


if __name__ == "__main__":
    main()
