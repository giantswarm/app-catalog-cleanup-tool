import datetime
import re
from typing import Dict, List, Optional

import pytest
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta

from app_catalog_cleanup_tool.splitters import (
    AppEntry,
    BaseSplitter,
    DateSplitter,
    LimitSplitter,
    PreReleaseSplitter,
    get_pre_release,
)

# noinspection PyUnresolvedReferences
from tests.test_helpers import Entries, test_entries, test_index_yaml  # noqa: F401


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
                    "linkerd2-app-0.1.1.tgz",
                    "linkerd2-app-0.0.0-25ecb7f4e6c03e719599e78c750047c931cafe1a.tgz",
                ],
                "loki-stack-app": ["loki-stack-app-0.1.0.tgz"],
            },
        ),
        # date: keep everything
        (
            DateSplitter(datetime.datetime.now(pytz.utc) - relativedelta(years=10)),
            {"linkerd2-app": [0, 1, 2], "loki-stack-app": [0]},
            {"linkerd2-app": [], "loki-stack-app": []},
        ),
        # date: keep 1 each
        (
            DateSplitter(parser.isoparse("2019-12-02 16:00Z")),
            {"linkerd2-app": [2], "loki-stack-app": []},
            {
                "linkerd2-app": ["linkerd2-app-0.1.0.tgz", "linkerd2-app-0.1.1.tgz"],
                "loki-stack-app": ["loki-stack-app-0.1.0.tgz"],
            },
        ),
        # limit: keep 1 each
        (
            LimitSplitter(1),
            {"linkerd2-app": [2], "loki-stack-app": []},
            {
                "linkerd2-app": ["linkerd2-app-0.1.0.tgz", "linkerd2-app-0.1.1.tgz"],
                "loki-stack-app": [],
            },
        ),
    ],
    ids=[
        "date: remove everything",
        "date: keep everything",
        "date: keep 1 each",
        "limit: keep 1 each",
    ],
)
def test_splitters(
    test_entries: Entries,  # noqa: F811
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


def _entry(version: str, created: str) -> AppEntry:
    return {"name": "app", "version": version, "created": created}


PRE_RELEASE_ENTRIES = [
    _entry("1.0.0", "2026-10-05T00:00:00Z"),
    _entry("1.0.0-rc.1", "2026-10-01T00:00:00Z"),
    _entry("1.0.0-rc.2", "2026-10-03T00:00:00Z"),
    _entry("0.9.0", "2026-09-01T00:00:00Z"),
    _entry("1.0.0+build.5", "2026-10-06T00:00:00Z"),
    _entry("0.9.0-gs1", "2026-09-02T00:00:00Z"),
    _entry("1.1.0-alpha.1+build.7", "2026-10-07T00:00:00Z"),
    _entry("v1.2.0-rc.3", "2026-10-08T00:00:00Z"),
    _entry("0.0.0-25ecb7f4e6c03e719599e78c750047c931cafe1a", "2026-10-09T00:00:00Z"),
]
ALL_PRE_RELEASES = re.compile(".*")
RC = re.compile(r"rc\.[0-9]+")


@pytest.mark.parametrize(
    "version,expected",
    [
        ("1.0.0-rc.1", "rc.1"),
        ("v1.0.0-rc.1", "rc.1"),
        ("1.1.0-alpha.1+build.7", "alpha.1"),
        ("1.22.2-gs2", "gs2"),
        ("0.0.0-25ecb7f4e6c03e719599e78c750047c931cafe1a", "25ecb7f4e6c03e719599e78c750047c931cafe1a"),
        ("1.0.0", None),
        ("v1.0.0", None),
        ("1.0.0+build.5", None),
        ("1.0", None),
        ("latest", None),
    ],
)
def test_get_pre_release(version: str, expected: Optional[str]) -> None:
    assert get_pre_release(version) == expected


@pytest.mark.parametrize(
    "splitter,exp_kept,exp_removed",
    [
        (
            PreReleaseSplitter(ALL_PRE_RELEASES),
            ["1.0.0", "0.9.0", "1.0.0+build.5"],
            [
                "app-1.0.0-rc.1.tgz",
                "app-1.0.0-rc.2.tgz",
                "app-0.9.0-gs1.tgz",
                "app-1.1.0-alpha.1+build.7.tgz",
                "app-v1.2.0-rc.3.tgz",
                "app-0.0.0-25ecb7f4e6c03e719599e78c750047c931cafe1a.tgz",
            ],
        ),
        (
            PreReleaseSplitter(RC),
            [
                "1.0.0",
                "0.9.0",
                "1.0.0+build.5",
                "0.9.0-gs1",
                "1.1.0-alpha.1+build.7",
                "0.0.0-25ecb7f4e6c03e719599e78c750047c931cafe1a",
            ],
            ["app-1.0.0-rc.1.tgz", "app-1.0.0-rc.2.tgz", "app-v1.2.0-rc.3.tgz"],
        ),
        (
            PreReleaseSplitter(RC, LimitSplitter(1)),
            [
                "1.0.0",
                "0.9.0",
                "1.0.0+build.5",
                "0.9.0-gs1",
                "1.1.0-alpha.1+build.7",
                "v1.2.0-rc.3",
                "0.0.0-25ecb7f4e6c03e719599e78c750047c931cafe1a",
            ],
            ["app-1.0.0-rc.1.tgz", "app-1.0.0-rc.2.tgz"],
        ),
        (
            PreReleaseSplitter(ALL_PRE_RELEASES, DateSplitter(parser.isoparse("2026-10-07T00:00:00Z"))),
            [
                "1.0.0",
                "0.9.0",
                "1.0.0+build.5",
                "1.1.0-alpha.1+build.7",
                "v1.2.0-rc.3",
                "0.0.0-25ecb7f4e6c03e719599e78c750047c931cafe1a",
            ],
            ["app-1.0.0-rc.1.tgz", "app-1.0.0-rc.2.tgz", "app-0.9.0-gs1.tgz"],
        ),
    ],
    ids=[
        "pre-release: remove all",
        "pre-release: remove rc only",
        "pre-release: keep 1 most recent rc",
        "pre-release: keep since date",
    ],
)
def test_pre_release_splitter(splitter: BaseSplitter, exp_kept: List[str], exp_removed: List[str]) -> None:
    keep, remove = splitter.split(PRE_RELEASE_ENTRIES)
    assert set(remove) == set(exp_removed)
    # stable versions always stay, every kept entry stays in its original order
    assert [e["version"] for e in keep] == [e["version"] for e in PRE_RELEASE_ENTRIES if e["version"] in exp_kept]
