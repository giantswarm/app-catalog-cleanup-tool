"""Main module."""
import asyncio
import logging

import configargparse

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
        help="A time delta (like '-3 days' or '-4 weeks') to keep catalog entries. Older entries matching also "
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
    return config


def validate(config: configargparse.Namespace) -> None:
    pass


async def main() -> None:
    config = configure()
    validate(config)
    await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
