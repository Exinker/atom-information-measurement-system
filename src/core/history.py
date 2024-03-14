from dataclasses import dataclass, field
from datetime import datetime

from .config import TrackedPath, TrackedPediod
from .scraper import Scraper
from .typing import AnalysisName, Frame, ProbeName, XMLPath


# --------        History        --------
@dataclass
class Record:
    analysis_name: AnalysisName = field(default='')
    probe_name: ProbeName = field(default='')
    dt: datetime = field(default_factory=lambda: datetime.fromtimestamp(0))


@dataclass
class History:
    records: Frame
    tracked_path: TrackedPath
    sep: str

    @property
    def last_analisys_name(self) -> AnalysisName:
        """Get the last `Record`'s analysis name."""

        # select data
        data = self.records[['analysis_name', 'dt']].copy(deep=True)
        data = data.set_index('dt', drop=False)
        data = data.sort_index()

        #
        if data.empty:
            return ''

        datum = data.iloc[-1]
        return datum['analysis_name']

    @property
    def last_record(self) -> Record:
        """Get the last `Record`."""

        # select data
        data = self.records[['analysis_name', 'probe_name', 'dt']].copy(deep=True)
        data = data.set_index('dt', drop=False)
        data = data.sort_index()

        #
        if data.empty:
            return Record()

        record = Record(**data.iloc[-1])
        return record

    def add(self) -> None:
        raise NotImplementedError

    def get_queue(self, analysis_name: AnalysisName, n: int = 1, ascending: bool = False) -> tuple[ProbeName]:
        """Get the `n` latest probe names for a given `analysis_name`."""

        # select from records
        cond = (self.records['analysis_name'] == analysis_name)
        data = self.records[cond][['probe_name', 'dt']].copy(deep=True)
        data = data.set_index('dt', drop=False)
        data = data.groupby(by='probe_name').max().sort_values(by='dt')

        if data.empty:
            return tuple()

        #
        probe_names = tuple(data.iloc[-n:].index)
        probe_names = probe_names if ascending else reversed(probe_names)
        return probe_names

    def get_index(self, analysis_name: AnalysisName, probe_name: ProbeName) -> tuple[XMLPath]:
        """Get filepaths of all `xml` files for a given analysis and probe's name."""

        # select from records
        cond = (self.records['analysis_name'] == analysis_name) & (self.records['probe_name'] == probe_name)
        data = self.records[cond][['analysis_name', 'probe_name', 'path']].copy(deep=True)

        #
        if data.empty:
            return tuple()

        paths = tuple(data['path'].unique())
        return paths

    # --------        handlers        --------
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
