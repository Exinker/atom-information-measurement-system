from datetime import datetime


from aims.config import Config, TrackedMode
from aims.core.history import History
from aims.core.sheets import ConvergenceByProbeSheet, SheetABC
from aims.core.sheets.sheets.workers import MultiprocessingWorker, Worker, WorkerABC
from aims.core.types import AnalysisName, ProbeName


class Sheets:

    def __init__(
        self,
        items: tuple[SheetABC],
    ) -> None:
        self.items = items

    @property
    def last_sheet(self) -> SheetABC | None:
        """Get the last recorded `sheet`."""
        try:
            return self.items[0]
        except IndexError:
            return SheetABC.from_default()

    @classmethod
    def create(
        cls,
        milestone: datetime,
        config: Config,
    ) -> 'Sheets':

        history = History.from_path(
            milestone=milestone,
            directory=config.directory,
            tracked_period=config.tracked_period,
            sep=config.sep,
        )

        tracked_analysis_name = _get_tracked_analysis_name(
            history=history,
            config=config,
        )
        tracked_probe_names = _get_tracked_probe_names(
            history=history,
            config=config,
            tracked_analysis_name=tracked_analysis_name,
        )

        worker = _get_worker(
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

    def __getitem__(self, i: int) -> SheetABC:
        return self.items[i]


def _get_tracked_analysis_name(
    history: History,
    config: Config,
) -> AnalysisName:
    return config.tracked_analisys_name or history.last_analisys_name


def _get_tracked_probe_names(
    history: History,
    config: Config,
    tracked_analysis_name: AnalysisName,
) -> tuple[ProbeName]:

    if config.tracked_probe_name:
        queue = history.get_queue(
            analysis_name=tracked_analysis_name,
            n=config.tracked_queue_length - 1,
        )
        return (config.tracked_probe_name, ) + queue

    return history.get_queue(
        analysis_name=tracked_analysis_name,
        n=config.tracked_queue_length,
    )


def _get_worker(
    config: Config,
) -> WorkerABC:

    match config.tracked_mode:
        case TrackedMode.CONVERGENCE_BY_PROBE:
            factory = ConvergenceByProbeSheet.from_history
        case _:
            raise NotImplementedError(f'Mode {config.tracked_mode} is not supported yet!')

    if config.n_workers > 1:
        return MultiprocessingWorker(
            factory=factory,
            n_workers=config.n_workers,
        )
    return Worker(
        factory=factory,
    )
