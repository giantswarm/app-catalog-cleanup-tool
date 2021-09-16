from typing import Dict, List

import pytest
import yaml

from app_catalog_cleanup_tool.splitters import AppEntry

Entries = Dict[str, List[AppEntry]]

TEST_CATALOG_PATH = "tests/assets"
TEST_INDEX_YAML_PATH = TEST_CATALOG_PATH + "/index.yaml"


@pytest.fixture
def test_index_yaml() -> str:
    with open("tests/assets/index.yaml", "r") as f:
        index_yaml = f.read()
    return index_yaml


@pytest.fixture
def test_entries(test_index_yaml: str) -> Entries:
    index_yaml = yaml.safe_load(test_index_yaml)
    return index_yaml["entries"]
