from __future__ import annotations

from importlib.resources import files
from logging import getLogger
from pathlib import Path
from string import Template
from subprocess import check_call
from typing import TYPE_CHECKING, cast

from utilities.platform import SYSTEM
from utilities.tempfile import TemporaryFile

from setup_cronjob.settings import SETTINGS

if TYPE_CHECKING:
    from pathlib import Path

    from utilities.types import PathLike

_LOGGER = getLogger(__name__)
_PACKAGE_ROOT = cast("Path", files("setup_cronjob"))


def setup_cronjob(
    *,
    name: str = SETTINGS.name,
    schedule: str = SETTINGS.schedule,
    user: str = SETTINGS.user,
    timeout: int = SETTINGS.timeout,
    kill_after: int = SETTINGS.kill_after,
    path_script: Path = SETTINGS.path_script,
    script_args: list[str] = SETTINGS.script_args,
    logs_keep: int = SETTINGS.logs_keep,
) -> None:
    """Set up a cronjob & logrotate."""
    if SYSTEM != "linux":
        msg = f"System must be 'linux'; got {SYSTEM!r}"
        raise TypeError(msg)
    _write_file(
        f"/etc/cron.d/{name}",
        _get_crontab(
            schedule=schedule,
            user=user,
            name=name,
            timeout=timeout,
            kill_after=kill_after,
            path_script=path_script,
            script_args=script_args,
        ),
    )
    _write_file(
        f"/etc/logrotate.d/{name}", _get_logrotate(name=name, logs_keep=logs_keep)
    )


def _get_crontab(
    *,
    schedule: str = SETTINGS.schedule,
    user: str = SETTINGS.user,
    name: str = SETTINGS.name,
    timeout: int = SETTINGS.timeout,
    kill_after: int = SETTINGS.kill_after,
    path_script: Path = SETTINGS.path_script,
    script_args: list[str] = SETTINGS.script_args,
) -> str:
    return Template((_PACKAGE_ROOT / "cron.tmpl").read_text()).substitute(
        SCHEDULE=schedule,
        USER=user,
        NAME=name,
        TIMEOUT=timeout,
        KILL_AFTER=kill_after,
        PATH_SCRIPT=path_script,
        SPACE=" " if len(script_args) >= 1 else "",
        SCRIPT_ARGS=" ".join(script_args),
    )


def _get_logrotate(
    *, name: str = SETTINGS.name, logs_keep: int = SETTINGS.logs_keep
) -> str:
    return Template((_PACKAGE_ROOT / "logrotate.tmpl").read_text()).substitute(
        NAME=name, ROTATE=logs_keep
    )


def _write_file(path: PathLike, text: str, /) -> None:
    _LOGGER.info("Writing '%s'...", path)
    with TemporaryFile() as src:
        _ = src.write_text(text)
        _ = check_call(["sudo", "mv", str(src), str(path)])
    _ = check_call(["sudo", "chown", "root:root", str(path)])
    _ = check_call(["sudo", "chmod", "u=rw,g=r,o=r", str(path)])
