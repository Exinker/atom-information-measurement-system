import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

from aims.config import Config
from aims.core.data.datum import DatumABC
from aims.core.history import ConvergenceByParallelsHistory
from aims.core.parsers.parsers import (
    AggregateByParallelsAtomDataParser,
    cache,
)
from aims.core.types import Frame, ProbeGUID, Series
from aims.core.utils.loaders import load_xml
from aims.settings import FilterLevel, SorterKind


@dataclass
class ConvergenceByParallelsDatum(DatumABC):
    probe_guid: ProbeGUID
    meta: Frame
    concentration: Frame
    targets: Frame
    levels: Series

    def filtrate(self, level: FilterLevel) -> 'DatumABC':
        """Filtrate `sheet` by selected level."""
        cls = self.__class__

        if self.levels.empty:  # no filtration
            return self

        columns = self.levels.index[self.levels >= level.value].to_list()
        return cls(
            probe_guid=self.probe_guid,
            meta=self.meta,
            concentration=self.concentration[columns],
            targets=self.targets[columns],
            levels=self.levels[columns],
        )

    def sort(self, kind: SorterKind) -> 'DatumABC':
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
            probe_guid=self.probe_guid,
            meta=self.meta,
            concentration=self.concentration[columns],
            targets=self.targets[columns],
            levels=self.levels[columns],
        )

    def select(self, columns: pd.Index) -> 'DatumABC':
        """Select from `sheet` by index."""
        cls = self.__class__

        return cls(
            probe_guid=self.probe_guid,
            meta=self.meta,
            concentration=self.concentration[columns],
            targets=self.targets[columns],
            levels=self.levels[columns],
        )

    def to_frame(self) -> Frame:
        return pd.concat([
            pd.concat([
                self.meta,
                self.concentration,
            ], axis=1),
            self.targets,
        ])

    @classmethod
    def from_history(
        cls,
        probe_guid: ProbeGUID,
        /,
        history: ConvergenceByParallelsHistory,
        config: Config,
    ) -> 'ConvergenceByParallelsDatum':
        """Get `sheet` from history."""
        filepath = history.get_filepath(
            probe_guid=probe_guid,
        )

        try:
            parser = AggregateByParallelsAtomDataParser(config=config)

            meta, concentration, statistics = _parse_atom_data(filepath, parser=parser)
            meta = pd.DataFrame(
                meta,
            ).reset_index(drop=True)
            concentration = pd.DataFrame(
                concentration,
            ).reset_index(drop=True)
            statistics = pd.DataFrame(
                statistics,
            ).reset_index(drop=True)
        except (ValueError, KeyError):
            return cls.from_default()

        nicknames = concentration.columns
        levels = pd.DataFrame(
            columns=nicknames,
        )

        values = pd.DataFrame(
            {},
            columns=nicknames,
        )
        for nickname in nicknames:
            values[nickname] = pd.to_numeric(concentration[nickname], errors='coerce')

        values = statistics.loc['ОСКО, %']
        levels = pd.Series(FilterLevel.NORMAL.value, index=values.index)
        levels[values.isna()] = FilterLevel.NOTSET.value
        levels[values >= 5] = FilterLevel.WARRING.value
        levels[values >= 10] = FilterLevel.DANGER.value

        return cls(
            probe_guid=probe_guid,
            meta=meta,
            concentration=concentration,
            targets=statistics,
            levels=levels,
        )


@cache
def _parse_atom_data(
    __filepath: str,
    parser: AggregateByParallelsAtomDataParser,
) -> tuple[Frame, Frame, Frame]:
    filedir, filename = os.path.split(__filepath)

    atom_data = parser.parse(
        xml=load_xml(__filepath),
    )

    meta = []
    reference = []
    concentration = []
    for index in atom_data.rows.index:
        meta.append({
            'file_dir': filedir,
            'file_name': filename,
            'datetime': atom_data.rows.loc[index, 'datetime'],
            'analysis_name': atom_data.meta.analysis_name,
            'organization_name': atom_data.meta.organization_name,
            'device_name': atom_data.meta.device_name,
            'user_name': atom_data.meta.user_name,
            'name': atom_data.rows.loc[index, 'name'],
            'is_certified': atom_data.rows.loc[index, 'is_certified'],
        })
        concentration.append(dict(
            **{
                str(nickname): values
                for nickname, values in atom_data.concentration.loc[index].to_dict().items()
            },
        ))
        reference.append(dict(
            **{
                str(symbol): value
                for symbol, value in atom_data.reference.loc[index].to_dict().items()
            },
        ))

    return pd.DataFrame(meta), pd.DataFrame(reference), pd.DataFrame(concentration)
