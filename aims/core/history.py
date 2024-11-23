from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from aims.config import Config, Directory, TrackedPediod
from aims.core.scrapers import Scraper
from aims.core.types import AnalysisName, Frame, ProbeGUID, ProbeName, XMLPath


@dataclass
class Record:
    analysis_name: AnalysisName = field(default='')
    probe_name: ProbeName = field(default='')
    probe_guid: ProbeGUID = field(default='')
    datetime: datetime = field(default_factory=lambda: datetime.fromtimestamp(0))


@dataclass
class HistoryABC(ABC):
    records: Frame
    milestone: datetime
    directory: Directory
    tracked_period: TrackedPediod
    sep: str

    datetime: datetime = field(default_factory=datetime.now)

    @property
    def last_analisys_name(self) -> AnalysisName:
        """Получить имя последнего анализа."""

        data = self.records[['analysis_name', 'datetime']].copy(deep=True)
        data = data.set_index('datetime', drop=False)
        data = data.sort_index()
        if data.empty:
            return ''

        return data.iloc[-1]['analysis_name']

    @property
    def last_record(self) -> Record | None:
        """Получить последний `record` в `history`."""

        data = self.records[['analysis_name', 'probe_name', 'probe_guid', 'datetime']].copy(deep=True)
        data = data.set_index('datetime', drop=False)
        data = data.sort_index()
        if data.empty:
            return None

        return Record(**data.iloc[-1])

    @abstractmethod
    def get_queue(
        self,
        analysis_name: AnalysisName,
        n: int = 1,
        ascending: bool = False,
    ) -> tuple[ProbeName, ...]:
        raise NotImplementedError


@dataclass
class ConvergenceByProbesHistory(HistoryABC):
    records: Frame
    milestone: datetime
    directory: Directory
    tracked_period: TrackedPediod
    sep: str

    datetime: datetime = field(default_factory=datetime.now)

    def get_tracked_analysis_name(
        self,
        config: Config,
    ) -> AnalysisName:
        return config.tracked_analisys_name or self.last_analisys_name

    def get_tracked_probe_names(
        self,
        config: Config,
        tracked_analysis_name: AnalysisName,
    ) -> tuple[ProbeName, ...]:

        if config.tracked_probe_name:
            queue = self.get_queue(
                analysis_name=tracked_analysis_name,
                n=config.tracked_queue_length - 1,
            )
            return (config.tracked_probe_name, ) + queue

        return self.get_queue(
            analysis_name=tracked_analysis_name,
            n=config.tracked_queue_length,
        )

    def get_queue(
        self,
        analysis_name: AnalysisName,
        n: int = 1,
        ascending: bool = False,
    ) -> tuple[ProbeName, ...]:
        """Получить очередь (последовательность `probe_names`) для выбранного `analysis_name` длинною не более `n`."""

        # select from records
        data = self.records[
            (self.records['analysis_name'] == analysis_name)
        ][['probe_name', 'datetime']].copy(deep=True)
        data = data.set_index('datetime', drop=False)
        data = data.groupby(by='probe_name').max().sort_values(by='datetime')
        if data.empty:
            return tuple()

        probe_names = tuple(data.iloc[-n:].index)
        probe_names = probe_names if ascending else reversed(probe_names)
        return tuple(probe_names)

    def get_filepaths(
        self,
        analysis_name: AnalysisName,
        probe_name: ProbeName,
    ) -> tuple[XMLPath, ...]:
        """Получить последовательность `filepaths` всех `xml` файлов files для выбранного `analysis_name` и `probe_name`."""

        records = self.records[
            (self.records['analysis_name'] == analysis_name) & (self.records['probe_name'] == probe_name)
        ].copy(deep=True)
        if records.empty:
            return tuple()

        return tuple(records['path'].unique())

    @classmethod
    def create(
        cls,
        milestone: datetime,
        directory: Directory,
        tracked_period: TrackedPediod,
        sep: str,
        verbose: bool = False,
    ) -> HistoryABC:
        """Получить `history` путем итеративного парсинга .xml файлов в заданной директории `directory`."""

        records = Scraper(
            milestone=milestone,
            directory=directory,
            tracked_period=tracked_period,
            sep=sep,
            verbose=verbose,
        ).scrape()

        return cls(
            records=records,
            milestone=milestone,
            directory=directory,
            tracked_period=tracked_period,
            sep=sep,
        )


@dataclass
class ConvergenceByParallelsHistory(HistoryABC):
    records: Frame
    milestone: datetime
    directory: Directory
    tracked_period: TrackedPediod
    sep: str

    datetime: datetime = field(default_factory=datetime.now)

    def get_tracked_probe_guids(
        self,
        config: Config,
    ) -> tuple[ProbeGUID, ...]:

        return self.get_queue(
            n=config.tracked_queue_length,
        )

    def get_queue(
        self,
        n: int = 1,
        ascending: bool = False,
    ) -> tuple[ProbeGUID, ...]:
        """Получить очередь (последовательность `probe_names`) для всех типов анализа длинною не более `n`."""

        # select from records
        data = self.records[['probe_name', 'probe_guid', 'datetime']].copy(deep=True)
        data = data.set_index('datetime', drop=False)
        data = data.groupby(by='probe_guid').max().sort_values(by='datetime')
        if data.empty:
            return tuple()

        probe_guids = tuple(data.index[-n:])
        probe_guids = probe_guids if ascending else reversed(probe_guids)
        return tuple(probe_guids)

    def get_filepath(
        self,
        probe_guid: ProbeGUID,
    ) -> XMLPath:
        """Получить последовательность `filepaths` всех `xml` файлов files для выбранного `probe_guid`."""

        records = self.records[
            (self.records['probe_guid'] == probe_guid)
        ].copy(deep=True)
        records = records.set_index('datetime', drop=False)
        records = records.groupby(by='probe_guid').max().sort_values(by='datetime')
        if records.empty:
            return tuple()

        return records['path'].item()

    @classmethod
    def create(
        cls,
        milestone: datetime,
        directory: Directory,
        tracked_period: TrackedPediod,
        sep: str,
        verbose: bool = False,
    ) -> HistoryABC:
        """Получить `history` путем итеративного парсинга .xml файлов в заданной директории `directory`."""

        records = Scraper(
            milestone=milestone,
            directory=directory,
            tracked_period=tracked_period,
            sep=sep,
            verbose=verbose,
        ).scrape()

        return cls(
            records=records,
            milestone=milestone,
            directory=directory,
            tracked_period=tracked_period,
            sep=sep,
        )
