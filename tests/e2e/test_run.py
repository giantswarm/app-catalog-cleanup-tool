import asyncio
import sys

from pytest_mock import MockerFixture

from app_catalog_cleanup_tool.__main__ import main


def test_run_catalog_cleanup(mocker: MockerFixture):
    mocker.patch.object(sys, "argv", ["bogus", "-l", "1", "-a", ".*", "tests/assets"])
    asyncio.run(main())
