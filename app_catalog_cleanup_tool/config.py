import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Pattern, Optional

import configargparse
import pytz
from dateutil import parser
from tempora import parse_timedelta

from app_catalog_cleanup_tool.splitters import BaseSplitter, DateSplitter, LimitSplitter, PreReleaseSplitter

VER = "v0.0.0-dev"
APP_NAME = "app_catalog_cleanup_tool"
CONFIG_FILE_PATH = ".app_catalog_cleanup_tool.yaml"

logger = logging.getLogger(__name__)


@dataclass
class ValidatedConfig:
    app_regexp: Pattern[str]
    path: str
    index_yaml: str
    dry_run: bool
    splitter: BaseSplitter


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
        "--dry-run",
        required=False,
        default=False,
        action="store_true",
        help="Enable dry-run (don't perform any real modifications).",
    )
    config_parser.add_argument(
        "-a",
        "--app-regexp",
        required=False,
        default=".*",
        help="Regexp of app names the cleanup will apply to.",
    )
    config_parser.add_argument(
        "-p",
        "--pre-release",
        required=False,
        help="Regexp the pre-release part of a semver version must fully match, like 'rc[.][0-9]+' for "
        "'1.0.0-rc.1' ('.*' matches every pre-release, versions like '1.0.0-gs1' included). Only matching "
        "pre-release entries are removed; every other version is kept. Alone, it removes every matching entry of "
        "the apps matching '--app-regexp'; combined with '--keep-since', '--delete-before' or '--limit-number', "
        "that condition applies to the matching entries only.",
    )
    exc_group = config_parser.add_mutually_exclusive_group(required=False)
    exc_group.add_argument(
        "-s",
        "--keep-since",
        help="A full date-time; catalog entries matching '--app-regexp' and older than this timestamp will be removed.",
    )
    exc_group.add_argument(
        "-b",
        "--delete-before",
        help="A time delta (like '3 days' or '4 weeks') to keep catalog entries. Older entries also matching "
        "'--app-regexp' will be removed.",
    )
    exc_group.add_argument(
        "-l",
        "--limit-number",
        help="For each entry matching '--app-regexp' only '-l' most recent version will be left "
        "(according to 'created' timestamp in 'index.yaml'.)",
    )
    config_parser.add_argument(
        "path",
        help="Path to the catalog directory.",
    )
    config_parser.add_argument("--version", action="version", version=f"{APP_NAME} {get_version()}")
    config = config_parser.parse_args()

    log_level = logging.DEBUG if config.debug else logging.INFO
    log_format = "%(asctime)s %(name)s %(levelname)s: %(message)s"
    logging.basicConfig(format=log_format, level=log_level)
    return config


def validate(config: configargparse.Namespace) -> Optional[ValidatedConfig]:
    try:
        # check if catalog dir exists
        if not config.path or not os.path.isdir(config.path) or not os.access(config.path, os.W_OK):
            raise ValueError(f"directory '{config.path}' not found")
        # check if index.yaml is there
        index_path = os.path.join(config.path, "index.yaml")
        if not os.path.isfile(index_path) or not os.access(index_path, os.W_OK) or not os.access(index_path, os.R_OK):
            raise ValueError(f"file 'index.yaml' doesn't exist in '{config.path}' or doesn't have RW permissions")
        # parse regexp
        try:
            app_regexp = re.compile(config.app_regexp)
        except re.error:
            raise ValueError(f"app name regexp '{config.app_regexp}' is not a valid regexp")

        splitter = get_splitter(config)
        return ValidatedConfig(
            app_regexp,
            config.path,
            os.path.join(config.path, "index.yaml"),
            config.dry_run,
            splitter,
        )

    except ValueError as e:
        logger.critical(f"Bad config: {e}.")
        return None


def get_splitter(config: configargparse.Namespace) -> BaseSplitter:
    splitter = get_condition_splitter(config)
    if config.pre_release:
        try:
            pre_release_regexp = re.compile(config.pre_release)
        except re.error:
            raise ValueError(f"pre-release regexp '{config.pre_release}' is not a valid regexp")
        return PreReleaseSplitter(pre_release_regexp, splitter)
    if splitter is None:
        raise ValueError(
            "one of the conditions '--pre-release', '--keep-since', '--delete-before' or '--limit-number' is required"
        )
    return splitter


def get_condition_splitter(config: configargparse.Namespace) -> Optional[BaseSplitter]:
    splitter: Optional[BaseSplitter]
    # parse since
    keep_from = datetime.now(timezone.utc)
    if config.keep_since:
        keep_from = parser.parse(config.keep_since)
        if not keep_from.tzinfo:
            keep_from = pytz.utc.localize(keep_from)
        splitter = DateSplitter(keep_from)
    # parse before
    elif config.delete_before:
        try:
            delta = parse_timedelta(config.delete_before)
        except Exception:
            raise ValueError(f"can't parse time delta '{config.delete_before}'")
        keep_from -= delta
        splitter = DateSplitter(keep_from)
    # parse limit
    elif config.limit_number:
        try:
            count = int(config.limit_number)
        except Exception:
            raise ValueError(f"can't parse limit count '{config.limit_number}'")
        splitter = LimitSplitter(count)
    else:
        splitter = None
    return splitter
