from dataclasses import dataclass, field
from datetime import datetime

from src.config import DEBUG, TrackedPath, TrackedPediod

from .scraper import Scraper
from .typing import AnalysisName, Frame, ProbeName, XMLPath


@dataclass
class Record:
    analysis_name: AnalysisName = field(default='')
    probe_name: ProbeName = field(default='')
    datetime: datetime = field(default_factory=lambda: datetime.fromtimestamp(0))


@dataclass
class History:
    records: Frame
    milestone: datetime
    tracked_path: TrackedPath
    tracked_period: TrackedPediod
    sep: str

    datetime: datetime = field(default_factory=datetime.now)

    @property
    def last_analisys_name(self) -> AnalysisName:
        """Получить имя последнего анализа."""

        # select data
        data = self.records[['analysis_name', 'datetime']].copy(deep=True)
        data = data.set_index('datetime', drop=False)
        data = data.sort_index()

        #
        if data.empty:
            return ''

        return data.iloc[-1]['analysis_name']

    @property
    def last_record(self) -> Record | None:
        """Получить последний `record` в `history`."""

        # select data
        data = self.records[['analysis_name', 'probe_name', 'datetime']].copy(deep=True)
        data = data.set_index('datetime', drop=False)
        data = data.sort_index()

        #
        if data.empty:
            return None

        return Record(**data.iloc[-1])

    # --------        handler        --------
    def get_queue(self, analysis_name: AnalysisName, n: int = 1, ascending: bool = False) -> tuple[ProbeName]:
        """Получить очередь (последовательность `probe_names`) для выбранного `analysis_name` длинною не более `n`."""

        # select from records
        data = self.records[
            (self.records['analysis_name'] == analysis_name)
        ][['probe_name', 'datetime']].copy(deep=True)
        data = data.set_index('datetime', drop=False)
        data = data.groupby(by='probe_name').max().sort_values(by='datetime')

        #
        if data.empty:
            return tuple()

        probe_names = tuple(data.iloc[-n:].index)
        probe_names = probe_names if ascending else reversed(probe_names)
        return probe_names

    def get_paths(self, analysis_name: AnalysisName, probe_name: ProbeName) -> tuple[XMLPath]:
        """Получить последовательность `filepaths` всех `xml` файлов files для выбранного `analysis_name` и `probe_name`."""

        records = self.records[
            (self.records['analysis_name'] == analysis_name) & (self.records['probe_name'] == probe_name)
        ].copy(deep=True)

        #
        if records.empty:
            return tuple()

        return tuple(records['path'].unique())

    # --------        factory        --------
    @classmethod
    def from_path(cls, milestone: datetime, tracked_path: TrackedPath, tracked_period: TrackedPediod, sep: str, verbose: bool = False) -> 'History':
        """Получить `history` путем итеративного парсинга .xml файлов в заданной директории `tracked_path`."""

        records = Scraper(
            milestone=milestone,
            tracked_path=tracked_path,
            tracked_period=tracked_period,
            sep=sep,
            verbose=verbose,
        ).parse()

        if DEBUG:
            print(records)

        #
        return cls(
            records=records,
            milestone=milestone,
            tracked_path=tracked_path,
            tracked_period=tracked_period,
            sep=sep,
        )
