import logging

import click
from modellogger.log_config import get_logger, configure_logging
from tests.example_top_library import top_library_function


@click.command()
@click.option("--debug", default=False, is_flag=True)
@click.option("--log-file", type=str, default=None)
def cli(debug, log_file):
    kwargs = {
        "app_name": "example_cli",
        "level": logging.DEBUG if debug else logging.INFO,
    }
    if log_file:
        kwargs["log_file"] = log_file
    configure_logging(**kwargs)
    logger = get_logger(__name__)
    click.echo("Hello World")
    logger.info("info in cli")
    logger.debug("debug in cli")
    top_library_function()


if __name__ == "__main__":
    cli()
