import datetime
from typing import Dict, List

import pytest
import pytz
import yaml
from app_catalog_cleanup_tool.splitters import DateSplitter, AppEntry, BaseSplitter
from dateutil import parser
from dateutil.relativedelta import relativedelta

Entries = Dict[str, List[AppEntry]]


@pytest.fixture
def test_entries() -> Entries:
    with open("tests/assets/test_index.yaml", "r") as f:
        index_yaml = yaml.safe_load(f.read())
    return index_yaml["entries"]


@pytest.mark.parametrize(
    "splitter,exp_keep_indexes,exp_remove_file_names",
    [
        # date: remove everything
        (
            DateSplitter(datetime.datetime.now(pytz.utc)),
            {"linkerd2-app": [], "loki-stack-app": []},
            {
                "linkerd2-app": [
                    "linkerd2-app-0.1.0.tgz",
                    "linkerd2-app-0.0.0-25ecb7f4e6c03e719599e78c750047c931cafe1a.tgz",
                ],
                "loki-stack-app": ["loki-stack-app-0.1.0.tgz"],
            },
        ),
        # date: keep everything
        (
            DateSplitter(datetime.datetime.now(pytz.utc) - relativedelta(years=10)),
            {"linkerd2-app": [0, 1], "loki-stack-app": [0]},
            {"linkerd2-app": [], "loki-stack-app": []},
        ),
        # date: keep 1 each
        (
            DateSplitter(parser.isoparse("2019-12-02 15:00Z")),
            {"linkerd2-app": [1], "loki-stack-app": []},
            {
                "linkerd2-app": ["linkerd2-app-0.1.0.tgz"],
                "loki-stack-app": ["loki-stack-app-0.1.0.tgz"],
            },
        ),
    ],
    ids=["date: remove everything", "date: keep everything", "date: keep 1 each"],
)
def test_splitters(
    test_entries: Entries,
    splitter: BaseSplitter,
    exp_keep_indexes: Dict[str, List[int]],
    exp_remove_file_names: Dict[str, List[str]],
) -> None:
    for app_name in test_entries:
        keep, remove = splitter.split(test_entries[app_name])
        assert set(remove) == set(exp_remove_file_names[app_name])
        len_diff = len(test_entries[app_name]) - len(keep)
        for index in exp_keep_indexes[app_name]:
            assert keep[index - len_diff] == test_entries[app_name][index]
