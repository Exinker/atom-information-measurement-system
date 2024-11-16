from abc import ABC, abstractmethod
from typing import Callable

from functools import partial
from multiprocessing import Pool

from aims.config import Config
from aims.core.history import History
from aims.core.sheets.base_sheet import SheetABC
from aims.core.types import AnalysisName, ProbeName


class WorkerABC(ABC):

    def __init__(
        self,
        factory: Callable[[History, AnalysisName, ProbeName, Config], SheetABC],
    ) -> None:
        self.factory = factory

    @abstractmethod
    def run(
        self,
        history: History,
        tracked_analysis_name: AnalysisName,
        tracked_probe_names: tuple[ProbeName],
        config: Config,
    ) -> tuple[SheetABC]:
        raise NotImplementedError


class Worker(WorkerABC):

    def __init__(
        self,
        factory: Callable[[History, AnalysisName, ProbeName, Config], SheetABC],
    ) -> None:
        super().__init__(factory=factory)

    def run(
        self,
        history: History,
        tracked_analysis_name: AnalysisName,
        tracked_probe_names: tuple[ProbeName],
        config: Config,
    ) -> tuple[SheetABC]:

        items = []
        for tracked_probe_name in tracked_probe_names:
            item = self.factory(
                history=history,
                analysis_name=tracked_analysis_name,
                probe_name=tracked_probe_name,
                config=config,
            )
            items.append(item)
        items = tuple(items)

        return items


class MultiprocessingWorker(WorkerABC):

    def __init__(
        self,
        factory: Callable[[History, AnalysisName, ProbeName, Config], SheetABC],
        n_workers: int,
    ) -> None:
        super().__init__(factory=factory)

        self.n_workers = n_workers

    def run(
        self,
        history: History,
        tracked_analysis_name: AnalysisName,
        tracked_probe_names: tuple[ProbeName],
        config: Config,
    ) -> tuple[SheetABC]:

        target = partial(
            self.factory,
            history,
            tracked_analysis_name,
            config=config,
        )
        with Pool(self.n_workers) as pool:
            items = pool.map(target, tracked_probe_names)
        items = tuple(items)

        return items
