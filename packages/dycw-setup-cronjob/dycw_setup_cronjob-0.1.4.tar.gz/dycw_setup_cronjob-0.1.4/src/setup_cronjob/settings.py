from __future__ import annotations

from pathlib import Path

from typed_settings import option, settings


@settings
class Settings:
    name: str = option(default="name", help="Cron job name")
    schedule: str = option(default="* * * * *", help="Cron job schedule")
    user: str = option(default="nonroot", help="Cron job user")
    timeout: int = option(default=60, help="Seconds until timing-out the cron job")
    kill_after: int = option(
        default=10, help="Seconds until killing the cron job (after timeout)"
    )
    path_script: Path = option(default=Path("script.py"), help="Path to the script")
    script_args: list[str] = option(factory=list, help="Script arguments")
    logs_keep: int = option(default=7, help="Number of logs to keep")
    dry_run: bool = option(default=False, help="Dry-run the CLI")


SETTINGS = Settings()


__all__ = ["SETTINGS", "Settings"]
