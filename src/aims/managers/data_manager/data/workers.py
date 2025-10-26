from abc import ABC, abstractmethod
from functools import partial
from multiprocessing import Pool
from typing import Callable

from aims.configs import Config, N_WORKERS, TrackedMode
from aims.managers.data_manager.data.datum import (
    ConvergenceByParallelsDatum,
    ConvergenceByProbesDatum,
    DatumABC,
)


class WorkerABC(ABC):

    def __init__(
        self,
        factory: Callable[[str, ...], DatumABC],
    ) -> None:
        self.factory = factory

    @abstractmethod
    def run(
        self,
        identifies: tuple[str, ...],
        /,
        **kwargs,
    ) -> tuple[DatumABC, ...]:
        raise NotImplementedError


class Worker(WorkerABC):

    def __init__(
        self,
        factory: Callable[[str, ...], DatumABC],
    ) -> None:
        super().__init__(factory=factory)

    def run(
        self,
        identifies: tuple[str, ...],
        /,
        **kwargs,
    ) -> tuple[DatumABC, ...]:

        items = []
        for identify in identifies:
            datum = self.factory(
                identify,
                **kwargs,
            )
            items.append(datum)

        return tuple(items)


class MultiprocessingWorker(WorkerABC):

    def __init__(
        self,
        factory: Callable[[str, ...], DatumABC],
        n_workers: int,
    ) -> None:
        super().__init__(factory=factory)

        self.n_workers = n_workers

    def run(
        self,
        identifies: tuple[str, ...],
        /,
        **kwargs,
    ) -> tuple[DatumABC, ...]:

        target = partial(
            self.factory,
            **kwargs,
        )
        with Pool(self.n_workers) as pool:
            items = pool.map(target, identifies)
        items = tuple(items)

        return items


def get_worker(
    config: Config,
) -> WorkerABC:

    match config.tracked_mode:
        case TrackedMode.CONVERGENCE_BY_PROBES:
            factory = ConvergenceByProbesDatum.from_index
        case TrackedMode.CONVERGENCE_BY_PARALLELS:
            factory = ConvergenceByParallelsDatum.from_index
        case _:
            raise NotImplementedError(f'Mode {config.tracked_mode} is not supported yet!')

    if N_WORKERS > 1:
        return MultiprocessingWorker(
            factory=factory,
            n_workers=N_WORKERS,
        )
    return Worker(
        factory=factory,
    )
