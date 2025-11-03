from datetime import datetime

from aims.configs import (
    Config,
    TrackedMode,
)

from .data import (
    ConvergenceByParallelsData,
    ConvergenceByProbesData,
    DataABC,
)


def data_factory(
    milestone: datetime,
    config: Config,
) -> DataABC:

    match config.tracked_mode:
        case TrackedMode.CONVERGENCE_BY_PROBES:
            return ConvergenceByProbesData.create(
                milestone=milestone,
                config=config,
            )
        case TrackedMode.CONVERGENCE_BY_PARALLELS:
            return ConvergenceByParallelsData.create(
                milestone=milestone,
                config=config,
            )
        case _:
            raise ValueError(f'Tracked mode: {config.tracked_mode} is not supported yet!')


__all__ = [
    ConvergenceByParallelsData,
    ConvergenceByProbesData,
    data_factory,
]
