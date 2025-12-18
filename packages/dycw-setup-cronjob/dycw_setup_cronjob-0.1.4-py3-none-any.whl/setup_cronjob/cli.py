from __future__ import annotations

from logging import getLogger

from click import command
from rich.pretty import pretty_repr
from typed_settings import click_options
from utilities.click import CONTEXT_SETTINGS_HELP_OPTION_NAMES

from setup_cronjob.lib import setup_cronjob
from setup_cronjob.settings import Settings

_LOGGER = getLogger(__name__)


@command(**CONTEXT_SETTINGS_HELP_OPTION_NAMES)
@click_options(Settings, "app", show_envvars_in_help=True)
def _main(settings: Settings, /) -> None:
    _LOGGER.info("Settings = %s", pretty_repr(settings))
    if settings.dry_run:
        _LOGGER.info("Dry-run; exiting...")
        return
    setup_cronjob(
        name=settings.name,
        schedule=settings.schedule,
        user=settings.user,
        timeout=settings.timeout,
        kill_after=settings.kill_after,
        path_script=settings.path_script,
        script_args=settings.script_args,
        logs_keep=settings.logs_keep,
    )


if __name__ == "__main__":
    _main()
