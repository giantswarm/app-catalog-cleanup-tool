"""Main module."""
import asyncio
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Pattern, Optional

import configargparse
from tempora import parse_timedelta

VER = "v0.0.0-dev"
APP_NAME = "app_catalog_cleanup_tool"
CONFIG_FILE_PATH = ".app_catalog_cleanup_tool.yaml"
logger = logging.getLogger(__name__)


def get_version() -> str:
    try:
        from .version import build_ver

        return build_ver
    except ImportError:
        return VER


def configure() -> configargparse.Namespace:
    config_parser = configargparse.ArgParser(
        prog=APP_NAME,
        add_config_file_help=True,
        default_config_files=[CONFIG_FILE_PATH],
        description="Cleanup old app catalog entries according to parameters.",
        add_env_var_help=True,
        auto_env_var_prefix="ACCT_",
        formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
        add_help=True,
    )
    config_parser.add_argument(
        "-d",
        "--debug",
        required=False,
        default=False,
        action="store_true",
        help="Enable debug messages.",
    )
    config_parser.add_argument(
        "-n",
        "--dry-mode",
        required=False,
        default=False,
        action="store_true",
        help="Enable dry-mode (don't perform any real modifications).",
    )
    config_parser.add_argument(
        "-a",
        "--app-regexp",
        required=False,
        default=".*",
        help="Regexp of app names the cleanup will apply to.",
    )
    exc_group = config_parser.add_mutually_exclusive_group(required=True)
    exc_group.add_argument(
        "-s",
        "--keep-since",
        help="A full date-time; catalog entries matching '--app-regexp' and older than this timestamp will be removed.",
    )
    exc_group.add_argument(
        "-b",
        "--delete-before",
        help="A time delta (like '3 days' or '4 weeks') to keep catalog entries. Older entries matching also "
        "'--arg-regexp' will be removed.",
    )
    config_parser.add_argument(
        "path",
        help="Path to the catalog directory.",
    )
    config_parser.add_argument(
        "--version", action="version", version=f"{APP_NAME} {get_version()}"
    )
    config = config_parser.parse_args()
    if config.debug:
        logger.setLevel(logging.DEBUG)
    return config


@dataclass
class ValidatedConfig:
    app_regexp: Pattern[str]
    keep_from: datetime


def validate(  # noqa :C901
    config: configargparse.Namespace,
) -> Optional[ValidatedConfig]:
    try:
        # check if catalog dir exists
        if (
            not config.path
            or not os.path.isdir(config.path)
            or not os.access(config.path, os.W_OK)
        ):
            raise ValueError(f"directory '{config.path}' not found")
        # check if index.yaml is there
        index_path = os.path.join(config.path, "index.yaml")
        if (
            not os.path.isfile(index_path)
            or not os.access(index_path, os.W_OK)
            or not os.access(index_path, os.R_OK)
        ):
            raise ValueError(
                f"file 'index.yaml' doesn't exists in '{config.path}' or doesn't have RW permissions"
            )
        # parse regexp
        try:
            app_regexp = re.compile(config.app_regexp)
        except re.error:
            raise ValueError(
                f"app name regexp '{config.app_regexp}' is not a valid regexp"
            )
        # parse since/before
        keep_from = datetime.now(timezone.utc)
        if config.keep_since:
            keep_from = datetime.fromisoformat(config.keep_since)
        if config.delete_before:
            try:
                delta = parse_timedelta(config.delete_before)
            except Exception:
                raise ValueError(f"can't parse time delta '{config.delete_before}'")
            keep_from -= delta
        return ValidatedConfig(app_regexp, keep_from)

    except ValueError as e:
        logger.critical(f"Bad config: {e}.")
        return None


async def main() -> None:
    config = configure()
    cfg = validate(config)
    if cfg is None:
        sys.exit(1)
    logger.info(f"Trying to remove all matching app entries before {cfg.keep_from}.")


if __name__ == "__main__":
    asyncio.run(main())
