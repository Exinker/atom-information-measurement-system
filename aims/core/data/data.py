from abc import ABC, abstractmethod
from datetime import datetime

from aims.config import Config
from aims.core.data.datum import DatumABC
from aims.core.data.workers import get_worker
from aims.core.history import (
    ConvergenceByParallelsHistory,
    ConvergenceByProbesHistory,
)


class DataABC(ABC):

    def __init__(
        self,
        items: tuple[DatumABC, ...],
    ) -> None:
        self.items = items

    @property
    def last_datum(self) -> DatumABC:
        try:
            return self.items[0]
        except IndexError:
            return DatumABC.from_default()

    @classmethod
    @abstractmethod
    def create(
        cls,
        milestone: datetime,
        config: Config,
    ) -> 'DataABC':
        raise NotImplementedError

    def __getitem__(self, i: int) -> DatumABC:
        return self.items[i]


class ConvergenceByProbesData(DataABC):

    @classmethod
    def create(
        cls,
        milestone: datetime,
        config: Config,
    ) -> 'ConvergenceByProbesData':

        history = ConvergenceByProbesHistory.create(
            milestone=milestone,
            directory=config.directory,
            tracked_period=config.tracked_period,
            sep=config.sep,
        )

        tracked_analysis_name = history.get_tracked_analysis_name(
            config=config,
        )
        tracked_probe_names = history.get_tracked_probe_names(
            config=config,
            tracked_analysis_name=tracked_analysis_name,
        )

        worker = get_worker(
            config=config,
        )
        items = worker.run(
            tracked_probe_names,
            analysis_name=tracked_analysis_name,
            history=history,
            config=config,
        )
        return cls(
            items=items,
        )


class ConvergenceByParallelsData(DataABC):

    @classmethod
    def create(
        cls,
        milestone: datetime,
        config: Config,
    ) -> 'ConvergenceByParallelsData':

        history = ConvergenceByParallelsHistory.create(
            milestone=milestone,
            directory=config.directory,
            tracked_period=config.tracked_period,
            sep=config.sep,
        )

        tracked_probe_guids = history.get_tracked_probe_guids(
            config=config,
        )

        worker = get_worker(
            config=config,
        )
        items = worker.run(
            tracked_probe_guids,
            history=history,
            config=config,
        )
        return cls(
            items=items,
        )
