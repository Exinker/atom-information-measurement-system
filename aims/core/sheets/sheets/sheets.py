from abc import ABC, abstractmethod
from datetime import datetime

from aims.config import Config
from aims.core.history import (
    ConvergenceByParallelsHistory,
    ConvergenceByProbesHistory,
)
from aims.core.sheets import SheetABC
from aims.core.sheets.sheets.utils import (
    get_tracked_analysis_name,
    get_tracked_probe_guids,
    get_tracked_probe_names,
    get_worker,
)


class SheetsABC(ABC):

    def __init__(
        self,
        items: tuple[SheetABC, ...],
    ) -> None:
        self.items = items

    @property
    def last_sheet(self) -> SheetABC:
        """Get the last recorded `sheet`."""
        try:
            return self.items[0]
        except IndexError:
            return SheetABC.from_default()

    @classmethod
    @abstractmethod
    def create(
        cls,
        milestone: datetime,
        config: Config,
    ) -> 'SheetsABC':
        raise NotImplementedError

    def __getitem__(self, i: int) -> SheetABC:
        return self.items[i]


class ConvergenceByProbesSheets(SheetsABC):

    @classmethod
    def create(
        cls,
        milestone: datetime,
        config: Config,
    ) -> 'ConvergenceByProbesSheets':

        history = ConvergenceByProbesHistory.create(
            milestone=milestone,
            directory=config.directory,
            tracked_period=config.tracked_period,
            sep=config.sep,
        )

        tracked_analysis_name = get_tracked_analysis_name(
            history=history,
            config=config,
        )
        tracked_probe_names = get_tracked_probe_names(
            history=history,
            config=config,
            tracked_analysis_name=tracked_analysis_name,
        )

        worker = get_worker(
            config=config,
        )
        items = worker.run(
            history=history,
            tracked_analysis_name=tracked_analysis_name,
            tracked_probe_names=tracked_probe_names,
            config=config,
        )
        return cls(
            items=items,
        )


class ConvergenceByParallelsSheets(SheetsABC):

    @classmethod
    def create(
        cls,
        milestone: datetime,
        config: Config,
    ) -> 'ConvergenceByParallelsSheets':

        history = ConvergenceByParallelsHistory.create(
            milestone=milestone,
            directory=config.directory,
            tracked_period=config.tracked_period,
            sep=config.sep,
        )

        tracked_probe_guids = get_tracked_probe_guids(
            history=history,
            config=config,
        )

        worker = get_worker(
            config=config,
        )
        items = worker.run(
            history=history,
            tracked_probe_guids=tracked_probe_guids,
            config=config,
        )
        return cls(
            items=items,
        )
