from dataclasses import dataclass, field
from datetime import datetime

from src.config import TrackedPath, TrackedPediod

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
    tracked_path: TrackedPath
    sep: str

    @property
    def last_analisys_name(self) -> AnalysisName:
        """Get the last analysis name."""

        # select data
        data = self.records[['analysis_name', 'datetime']].copy(deep=True)
        data = data.set_index('datetime', drop=False)
        data = data.sort_index()

        #
        if data.empty:
            return ''

        datum = data.iloc[-1]
        return datum['analysis_name']

    @property
    def last_record(self) -> Record | None:
        """Get the last `Record`."""

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
        """Get the `n` latest probe names for a given `analysis_name`."""

        # select from records
        cond = (self.records['analysis_name'] == analysis_name)
        data = self.records[cond][['probe_name', 'datetime']].copy(deep=True)
        data = data.set_index('datetime', drop=False)
        data = data.groupby(by='probe_name').max().sort_values(by='datetime')

        if data.empty:
            return tuple()

        #
        probe_names = tuple(data.iloc[-n:].index)
        probe_names = probe_names if ascending else reversed(probe_names)
        return probe_names

    def get_paths(self) -> tuple[XMLPath]:
        """Get filepaths of all `xml` files for a given analysis and probe's name."""

        if self.records.empty:
            return tuple()

        return tuple(self.records['path'].unique())

    # --------        factory        --------
    def select(self, analysis_name: AnalysisName, probe_name: ProbeName) -> 'History':

        cond = (self.records['analysis_name'] == analysis_name) & (self.records['probe_name'] == probe_name)
        records = self.records[cond].copy(deep=True)

        #
        return self.__class__(
            records=records,
            tracked_path=self.tracked_path,
            sep=self.sep,
        )

    @classmethod
    def from_path(cls, tracked_path: TrackedPath, tracked_period: TrackedPediod, sep: str, verbose: bool = False) -> 'History':
        """Get history for a given path by iterable walk."""

        scraper = Scraper(
            tracked_path=tracked_path,
            tracked_period=tracked_period,
            sep=sep,
            verbose=verbose,
        )

        #
        return cls(
            records=scraper.parse(),
            tracked_path=tracked_path,
            sep=sep,
        )
