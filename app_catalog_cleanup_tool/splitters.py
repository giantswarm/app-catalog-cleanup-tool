import logging
import re
from abc import abstractmethod, ABC
from datetime import datetime
from typing import Any, NamedTuple, List, Dict, Optional, Pattern

from dateutil import parser

logger = logging.getLogger(__name__)

AppEntry = Dict[str, Any]

# A semver 2.0.0 version with a pre-release part, like '1.0.0-rc.1' or '0.0.0-25ecb7f4'; a leading 'v' is accepted.
PRE_RELEASE_VERSION = re.compile(r"v?\d+\.\d+\.\d+-(?P<pre_release>[0-9A-Za-z.-]+)(\+[0-9A-Za-z.-]+)?")


def get_pre_release(version: str) -> Optional[str]:
    """Returns the pre-release part of a semver version ('rc.1' for '1.0.0-rc.1+build.2'), None for any other."""
    match = PRE_RELEASE_VERSION.fullmatch(str(version))
    return match.group("pre_release") if match else None


class SplitResult(NamedTuple):
    to_keep: List[AppEntry]
    to_remove: List[str]


class BaseSplitter(ABC):
    @abstractmethod
    def split(self, entries: List[AppEntry]) -> SplitResult:
        raise NotImplementedError()

    def _get_chart_file_name(self, entry: AppEntry) -> str:
        return f"{entry['name']}-{entry['version']}.tgz"


class DateSplitter(BaseSplitter):
    def __init__(self, keep_from_date: datetime):
        self._keep_from_date = keep_from_date
        logger.info(f"Trying to remove all matching app entries before {keep_from_date}.")

    def split(self, entries: List[AppEntry]) -> SplitResult:
        def keep(date: str) -> bool:
            return parser.isoparse(date) >= self._keep_from_date

        new_app_entries = [e for e in entries if keep(e["created"])]
        entries_to_remove = [self._get_chart_file_name(e) for e in entries if not keep(e["created"])]

        return SplitResult(new_app_entries, entries_to_remove)


class LimitSplitter(BaseSplitter):
    def __init__(self, keep_count: int):
        self._keep_count = keep_count
        logger.info(f"Trying to remove all matching app entries to limit them to max {keep_count} each.")

    def split(self, entries: List[AppEntry]) -> SplitResult:
        srt = sorted(entries, key=lambda e: parser.isoparse(e["created"]), reverse=True)
        new_app_entries = srt[: self._keep_count]
        entries_to_remove = [self._get_chart_file_name(e) for e in srt[self._keep_count :]]
        return SplitResult(new_app_entries, entries_to_remove)


class PreReleaseSplitter(BaseSplitter):
    """Applies a splitter to the pre-release entries whose pre-release part fully matches the regexp only, and
    keeps every other entry.

    Without an inner splitter, all matching pre-release entries are removed.
    """

    def __init__(self, pre_release_regexp: Pattern[str], inner: Optional[BaseSplitter] = None):
        self._pre_release_regexp = pre_release_regexp
        self._inner = inner
        logger.info(f"Limiting the removal to pre-release versions matching '{pre_release_regexp.pattern}'.")

    def _matches(self, entry: AppEntry) -> bool:
        pre_release = get_pre_release(entry["version"])
        return pre_release is not None and self._pre_release_regexp.fullmatch(pre_release) is not None

    def split(self, entries: List[AppEntry]) -> SplitResult:
        pre_releases = [e for e in entries if self._matches(e)]
        if self._inner is None:
            kept_pre_releases: List[AppEntry] = []
            entries_to_remove = [self._get_chart_file_name(e) for e in pre_releases]
        else:
            kept_pre_releases, entries_to_remove = self._inner.split(pre_releases)
        kept_ids = {id(e) for e in kept_pre_releases}
        new_app_entries = [e for e in entries if not self._matches(e) or id(e) in kept_ids]
        return SplitResult(new_app_entries, entries_to_remove)
