from datetime import datetime

from aims.config import (
    Config,
    TrackedMode,
)

from .sheets import (
    ConvergenceByParallelsSheets,
    ConvergenceByProbesSheets,
    SheetsABC,
)


def sheets_factory(
    milestone: datetime,
    config: Config,
) -> SheetsABC:
    match config.tracked_mode:
        case TrackedMode.CONVERGENCE_BY_PROBES:
            return ConvergenceByProbesSheets.create(
                milestone=milestone,
                config=config,
            )
        case TrackedMode.CONVERGENCE_BY_PARALLELS:
            return ConvergenceByParallelsSheets.create(
                milestone=milestone,
                config=config,
            )
        case _:
            raise ValueError(f'Tracked mode: {config.tracked_mode} is not supported yet!')


__all__ = [
    ConvergenceByParallelsSheets,
    ConvergenceByProbesSheets,
    sheets_factory,
]
