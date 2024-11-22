from aims.config import Config, TrackedMode
from aims.core.history import (
    ConvergenceByProbesHistory,
    ConvergenceByParallelsHistory,
)
from aims.core.sheets import (
    ConvergenceByParallelsSheet,
    ConvergenceByProbesSheet,
)
from aims.core.sheets.sheets.workers import MultiprocessingWorker, Worker, WorkerABC
from aims.core.types import AnalysisName, ProbeGUID, ProbeName


def get_tracked_analysis_name(
    history: ConvergenceByProbesHistory,
    config: Config,
) -> AnalysisName:
    return config.tracked_analisys_name or history.last_analisys_name


def get_tracked_probe_names(
    history: ConvergenceByProbesHistory,
    config: Config,
    tracked_analysis_name: AnalysisName,
) -> tuple[ProbeName, ...]:

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


def get_tracked_probe_guids(
    history: ConvergenceByParallelsHistory,
    config: Config,
) -> tuple[ProbeGUID, ...]:

    return history.get_queue(
        n=config.tracked_queue_length,
    )


def get_worker(
    config: Config,
) -> WorkerABC:

    match config.tracked_mode:
        case TrackedMode.CONVERGENCE_BY_PROBES:
            factory = ConvergenceByProbesSheet.from_history
        case TrackedMode.CONVERGENCE_BY_PARALLELS:
            factory = ConvergenceByParallelsSheet.from_history
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
