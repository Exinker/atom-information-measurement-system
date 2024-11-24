from abc import abstractmethod
from dataclasses import dataclass

import pandas as pd

from aims.config import Config
from aims.core.history import HistoryABC
from aims.core.types import AnalysisName, Frame, ProbeName, Series


@dataclass
class DatumABC:
    meta: Frame
    concentration: Frame
    targets: Frame
    levels: Series

    @property
    def last_meta(self) -> Series | None:
        """Get the last recorded probe's meta `Series`."""

        meta = self.meta.copy(deep=True)
        meta = meta.set_index('datetime', drop=False)
        meta = meta.sort_index()

        if meta.empty:
            return None
        return meta.iloc[-1]

    def to_frame(self) -> Frame:
        return pd.concat([
            pd.concat([
                self.meta,
                self.concentration,
            ], axis=1),
            self.targets,
        ])

    @classmethod
    def from_default(
        cls,
    ) -> 'DatumABC':
        """Get empty `sheet`."""

        return cls(
            meta=pd.DataFrame({}, columns=[
                'file_dir',
                'file_name',
                'datetime',
                'analysis_name',
                'organization_name',
                'device_name',
                'user_name',
                'name',
                'is_certified',
            ]),
            concentration=pd.DataFrame(),
            targets=pd.DataFrame(),
            levels=pd.Series(),
        )

    @classmethod
    @abstractmethod
    def from_history(
        cls,
        history: HistoryABC,
        analysis_name: AnalysisName,
        probe_name: ProbeName,
        config: Config,
    ) -> 'DatumABC':
        """Get `sheet` from history."""

        raise NotImplementedError
