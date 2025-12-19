from __future__ import annotations

from click import command
from rich.pretty import pretty_repr
from typed_settings import click_options
from utilities.click import CONTEXT_SETTINGS_HELP_OPTION_NAMES
from utilities.logging import basic_config

from uv_publish import __version__
from uv_publish.lib import uv_publish
from uv_publish.logging import LOGGER
from uv_publish.settings import Settings


@command(**CONTEXT_SETTINGS_HELP_OPTION_NAMES)
@click_options(Settings, "app", show_envvars_in_help=True)
def _main(settings: Settings, /) -> None:
    if settings.dry_run:
        LOGGER.info("Dry run; exiting...")
        return
    basic_config(obj=LOGGER)
    LOGGER.info(
        "Running version %s with settings:\n%s...", __version__, pretty_repr(settings)
    )
    uv_publish(trusted_publishing=settings.trusted_publishing)


if __name__ == "__main__":
    _main()
