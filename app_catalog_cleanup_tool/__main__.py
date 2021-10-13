"""Main module."""
import asyncio
import logging
import os
import shutil
import sys
from copy import deepcopy
from typing import List

import aiofiles
import aiofiles.os
from ruamel.yaml import YAML

from app_catalog_cleanup_tool.config import ValidatedConfig, configure, validate

logger = logging.getLogger(__name__)


async def clean_catalog(cfg: ValidatedConfig) -> None:
    to_remove = await clean_index(cfg)
    if not cfg.dry_run:
        del_tasks = [
            aiofiles.os.remove(os.path.join(cfg.path, name))
            for name in to_remove
            if os.path.exists(os.path.join(cfg.path, name))
        ]
        await asyncio.gather(*del_tasks)
    # TODO: the part below would probably also benefit a little from running as async, but `aiofiles` doesn't
    #  currently provide `rmtree`, only `rmdir`, so skipping for now
    for name in to_remove:
        logger.debug(f"Removed chart file: '{name}'.")
        meta_dir_name = os.path.join(cfg.path, name + "-meta")
        if not os.path.isdir(meta_dir_name):
            continue
        logger.debug(f"Removing directory: '{os.path.basename(meta_dir_name)}'.")
        if not cfg.dry_run:
            shutil.rmtree(meta_dir_name)


async def clean_index(cfg: ValidatedConfig) -> List[str]:
    yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    yaml.preserve_quotes = True

    async with aiofiles.open(cfg.index_yaml, mode="r") as f:
        raw_yaml = await f.read()
        index_yaml = yaml.load(raw_yaml)
    to_remove = []
    entries = index_yaml["entries"]
    logger.debug(f"Loaded {len(entries)} app entries from the catalog index.")
    new_index_yaml = deepcopy(index_yaml)
    new_entries = new_index_yaml["entries"]
    for app_name in index_yaml["entries"].keys():
        if not cfg.app_regexp.fullmatch(app_name):
            logger.debug(f"Skipping app '{app_name}' as it doesn't match the configured app name regexp.")
            continue
        del new_entries[app_name]
        before = len(entries[app_name])
        new_app_entries, entries_to_remove = cfg.splitter.split(entries[app_name])
        if len(new_app_entries) > 0:
            new_entries[app_name] = new_app_entries
        if len(entries_to_remove) > 0:
            to_remove.extend(entries_to_remove)
        after = len(new_app_entries)
        logger.info(f"App '{app_name}' number of versions will be trimmed to {after} from {before}.")

    # save backup and the new file
    if not cfg.dry_run:
        shutil.move(cfg.index_yaml, cfg.index_yaml + ".back")
        async with aiofiles.open(cfg.index_yaml, mode="w") as f:
            import io

            new_index_yaml_io = io.StringIO()

            yaml.dump(new_index_yaml, new_index_yaml_io)
            await f.write(new_index_yaml_io.getvalue())

    return to_remove


async def main() -> None:
    config = configure()
    cfg = validate(config)
    if cfg is None:
        sys.exit(1)
    if cfg.dry_run:
        logger.warning("Running in dry-run, no real operations will be performed.")
    await clean_catalog(cfg)
    logger.info("Catalog cleanup complete.")


if __name__ == "__main__":
    # Please note: this piece of code is written as async/await mostly for learning purposes. It offers
    #  some performance speedups as well. If you don't like it, shout at me.
    asyncio.run(main())
