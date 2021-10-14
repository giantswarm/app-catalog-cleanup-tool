import asyncio
import sys
from typing import cast
from unittest.mock import call, Mock, AsyncMock, MagicMock

from pytest_mock import MockerFixture

import app_catalog_cleanup_tool
from app_catalog_cleanup_tool.__main__ import main

# noinspection PyUnresolvedReferences
from tests.test_helpers import (  # noqa: F401
    TEST_INDEX_YAML_PATH,
    test_index_yaml,
    TEST_CATALOG_PATH,
)


def test_run_catalog_cleanup(mocker: MockerFixture, test_index_yaml: str):  # noqa: F811
    mocker.patch.object(sys, "argv", ["bogus", "-l", "1", "-a", ".*", "tests/assets"])
    mocker.patch("app_catalog_cleanup_tool.__main__.shutil.move")
    mocker.patch("app_catalog_cleanup_tool.__main__.shutil.rmtree")
    mocker.patch("app_catalog_cleanup_tool.__main__.aiofiles.os.remove", name="aio_remove")

    mocker.patch("app_catalog_cleanup_tool.__main__.os.path.isdir")

    mocker.patch("app_catalog_cleanup_tool.__main__.aiofiles.open")
    async_open_mock = cast(AsyncMock, app_catalog_cleanup_tool.__main__.aiofiles.open)
    index_file_mock = mocker.AsyncMock(name="index file")
    index_file_mock.read.return_value = test_index_yaml
    async_open_mock.return_value.__aenter__.return_value = index_file_mock

    asyncio.run(main())

    # index.yaml was read
    assert async_open_mock.call_args_list[0] == call(TEST_INDEX_YAML_PATH, mode="r")
    # backup of index.yaml was saved
    cast(Mock, app_catalog_cleanup_tool.__main__.shutil.move).assert_called_once_with(
        TEST_INDEX_YAML_PATH, TEST_INDEX_YAML_PATH + ".back"
    )
    # new index.yaml was written
    assert async_open_mock.call_args_list[1] == call(TEST_INDEX_YAML_PATH, mode="w")
    assert async_open_mock.call_count == 2
    # required chart file was removed
    # os.remove should not be executed for nonexisting `linkerd2-app-0.1.1.tgz`
    aio_remove_mock = cast(AsyncMock, app_catalog_cleanup_tool.__main__.aiofiles.os.remove)
    aio_remove_mock.assert_called_once_with(TEST_CATALOG_PATH + "/linkerd2-app-0.1.0.tgz")

    # meta dir was removed
    rmtree_mock = cast(MagicMock, app_catalog_cleanup_tool.__main__.shutil.rmtree)
    rmtree_mock.assert_has_calls(
        [
            call(TEST_CATALOG_PATH + "/linkerd2-app-0.1.0.tgz-meta"),
            call(TEST_CATALOG_PATH + "/linkerd2-app-0.1.1.tgz-meta"),
        ],
        any_order=True,
    )
