from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import pandas as pd

from aims.config import Config
from aims.core.history import History
from aims.core.types import AnalysisName, Frame, ProbeName, Series
from aims.settings import FilterLevel, SorterKind


@dataclass
class SheetABC:
    analysis_name: AnalysisName
    probe_name: ProbeName
    meta: Frame
    prediction: Frame
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

    # --------        handlers        --------
    def filtrate(self, level: FilterLevel) -> 'SheetABC':
        """Filtrate `sheet` by selected level."""
        cls = self.__class__

        if self.levels.empty:  # no filtration
            return self

        columns = self.levels.index[self.levels >= level.value].to_list()
        return cls(
            analysis_name=self.analysis_name,
            probe_name=self.probe_name,
            meta=self.meta,
            prediction=self.prediction[columns],
            targets=self.targets[columns],
            levels=self.levels[columns],
        )

    def sort(self, kind: SorterKind) -> 'SheetABC':
        """Sort `sheet` by selected kind."""
        cls = self.__class__

        match kind:
            case SorterKind.NONE:
                columns = self.targets.columns
            case SorterKind.FILTER_LEVEL:
                columns = self.targets.columns[np.argsort(-self.levels)]
            case _:
                raise NotImplementedError

        return cls(
            analysis_name=self.analysis_name,
            probe_name=self.probe_name,
            meta=self.meta,
            prediction=self.prediction[columns],
            targets=self.targets[columns],
            levels=self.levels[columns],
        )

    def select(self, columns: pd.Index) -> 'SheetABC':
        """Select from `sheet` by index."""
        cls = self.__class__

        return cls(
            analysis_name=self.analysis_name,
            probe_name=self.probe_name,
            meta=self.meta,
            prediction=self.prediction[columns],
            targets=self.targets[columns],
            levels=self.levels[columns],
        )

    def to_frame(self) -> Frame:
        return pd.concat([
            pd.concat([
                self.meta,
                self.prediction,
            ], axis=1),
            self.targets,
        ])

    @classmethod
    def from_default(
        cls,
        analysis_name: AnalysisName = '',
        probe_name: ProbeName = '',
    ) -> 'SheetABC':
        """Get empty `sheet`."""

        return cls(
            analysis_name=analysis_name,
            probe_name=probe_name,
            meta=pd.DataFrame({}, columns=[
                'file_dir',
                'file_name',
                'datetime',
                'analysis_name',
                'organization_name',
                'device_name',
                'user_name',
                'probe_name',
                'is_certified',
            ]),
            prediction=pd.DataFrame(),
            targets=pd.DataFrame(),
            levels=pd.Series(),
        )

    @classmethod
    @abstractmethod
    def from_history(
        cls,
        history: History,
        analysis_name: AnalysisName,
        probe_name: ProbeName,
        config: Config,
    ) -> 'SheetABC':
        """Get `sheet` from history."""

        raise NotImplementedError
