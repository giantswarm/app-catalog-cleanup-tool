from typing import Dict, List

import pytest
import yaml

from app_catalog_cleanup_tool.splitters import AppEntry

Entries = Dict[str, List[AppEntry]]


@pytest.fixture
def test_entries() -> Entries:
    with open("tests/assets/index.yaml", "r") as f:
        index_yaml = yaml.safe_load(f.read())
    return index_yaml["entries"]
