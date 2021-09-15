import logging
from abc import abstractmethod, ABC
from datetime import datetime
from typing import Any, NamedTuple, List, Dict

from dateutil import parser

logger = logging.getLogger(__name__)

AppEntry = Dict[str, Any]


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
        logger.info(
            f"Trying to remove all matching app entries before {keep_from_date}."
        )

    def split(self, entries: List[AppEntry]) -> SplitResult:
        def keep(date: str) -> bool:
            return parser.isoparse(date) >= self._keep_from_date

        new_app_entries = [e for e in entries if keep(e["created"])]
        entries_to_remove = [
            self._get_chart_file_name(e) for e in entries if not keep(e["created"])
        ]

        return SplitResult(new_app_entries, entries_to_remove)


class LimitSplitter(BaseSplitter):
    def __init__(self, keep_count: int):
        self._keep_count = keep_count
        logger.info(
            f"Trying to remove all matching app entries to limit them to max {keep_count} each."
        )

    def split(self, entries: List[AppEntry]) -> SplitResult:
        srt = sorted(entries, key=lambda e: parser.isoparse(e["created"]), reverse=True)
        new_app_entries = srt[: self._keep_count]
        entries_to_remove = [
            self._get_chart_file_name(e) for e in srt[self._keep_count :]
        ]
        return SplitResult(new_app_entries, entries_to_remove)
