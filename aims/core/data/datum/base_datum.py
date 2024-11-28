from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, TypeAlias

import numpy as np
import pandas as pd

from aims.config import Config
from aims.core.index import IndexABC
from aims.core.types import AnalysisName, ProbeName, Series
from aims.settings import FilterLevel, SorterKind


DatumSheet: TypeAlias = pd.DataFrame


@dataclass
class DatumMeta:
    analysis_name: AnalysisName
    probe_name: ProbeName
    organization_name: str
    device_name: str
    user_name: str
    datetime: datetime


@dataclass
class DatumABC:
    sheet: DatumSheet
    meta: DatumMeta
    levels: Series

    META_COLUMN_NAMES: ClassVar[list[str]] = []
    META_COLUMN_NAMES_VISIBLE: ClassVar[list[str]] = []
    TARGET_ROW_NAMES: ClassVar[list[str]] = []

    def filtrate(self, level: FilterLevel) -> 'DatumABC':
        """Filtrate `sheet` by selected level."""
        cls = self.__class__

        if self.levels.empty:  # no filtration
            return self

        columns = self.levels.index[self.levels >= level.value].to_list()
        return cls(
            sheet=self.sheet[cls.META_COLUMN_NAMES + columns],
            meta=self.meta,
            levels=self.levels[columns],
        )

    def sort(self, kind: SorterKind) -> 'DatumABC':
        """Sort `sheet` by selected kind."""
        cls = self.__class__

        match kind:
            case SorterKind.NONE:
                columns = self.levels.index.to_list()
            case SorterKind.FILTER_LEVEL:
                columns = self.levels.index[np.argsort(-self.levels)].to_list()
            case _:
                raise NotImplementedError

        return cls(
            sheet=self.sheet[cls.META_COLUMN_NAMES + columns],
            meta=self.meta,
            levels=self.levels[columns],
        )

    def select(self, columns: pd.Index) -> 'DatumABC':
        """Select from `sheet` by index."""
        cls = self.__class__

        return cls(
            sheet=self.sheet[cls.META_COLUMN_NAMES + columns.to_list()],
            meta=self.meta,
            levels=self.levels[columns],
        )

    @classmethod
    def from_default(
        cls,
    ) -> 'DatumABC':
        """Get empty `sheet`."""

        return cls(
            sheet=pd.DataFrame(
                columns=cls.META_COLUMN_NAMES,
            ),
            meta=DatumMeta(
                analysis_name='',
                probe_name='',
                organization_name='',
                device_name='',
                user_name='',
                datetime=datetime.now(),
            ),
            levels=pd.Series(),
        )

    @classmethod
    @abstractmethod
    def from_index(
        cls,
        index: IndexABC,
        analysis_name: AnalysisName,
        probe_name: ProbeName,
        config: Config,
    ) -> 'DatumABC':
        """Get `sheet` from index."""

        raise NotImplementedError
