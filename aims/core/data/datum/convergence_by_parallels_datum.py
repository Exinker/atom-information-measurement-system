import logging
import os
from dataclasses import dataclass
from typing import ClassVar

import numpy as np
import pandas as pd

from aims.config import Config
from aims.core.atom_data import AtomData
from aims.core.data.datum import (
    DatumABC,
    DatumMeta,
    DatumSheet,
)
from aims.core.history import ConvergenceByParallelsHistory
from aims.core.parsers import (
    AggregateByParallelsAtomDataParser,
    cache,
)
from aims.core.types import Frame, ProbeGUID, Series
from aims.core.utils.loaders import load_xml
from aims.settings import FilterLevel


LOGGER = logging.getLogger('app')

META_COLUMN_NAMES = [
    'filepath',
    'datetime',
    'organization_name',
    'device_name',
    'user_name',
    'analysis_name',
    'probe_guid',
    'probe_name',
    'is_certified',
    'parallel_name',
]
TARGET_ROW_NAMES = [
    'Cред.',
    'СКО',
]


@dataclass
class ConvergenceByParallelsDatum(DatumABC):
    sheet: DatumSheet
    meta: DatumMeta
    levels: Series

    META_COLUMN_NAMES: ClassVar = META_COLUMN_NAMES
    META_COLUMN_NAMES_VISIBLE: ClassVar = ['parallel_name']
    TARGET_ROW_NAMES: ClassVar = TARGET_ROW_NAMES

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

            # parse
            atom_data = _parse_atom_data(filepath, parser=parser)

            # filtrate
            n_parallels = atom_data.meta.shape[0]

            cond = np.full(n_parallels, True)
            for j in range(n_parallels):

                cond[j] = cond[j] and config.tracked_period.check(
                    atom_data.meta.iloc[j]['datetime'],
                    milestone=history.milestone,
                )
        except (ValueError, KeyError) as error:
            LOGGER.warning('Atom data parse faild with error: %s', error)
            return cls.from_default()

        values = atom_data.statistics.loc['СКО']
        levels = pd.Series(FilterLevel.NORMAL.value, index=values.index)
        levels[values.isna()] = FilterLevel.NOTSET.value

        return cls(
            sheet=pd.concat([
                pd.concat([
                    atom_data.meta,
                    atom_data.concentration,
                ], axis=1),
                atom_data.statistics,
            ]),
            meta=DatumMeta(
                analysis_name=atom_data.meta['analysis_name'].unique().item(),
                probe_name=atom_data.meta['probe_name'].unique().item(),
                organization_name=atom_data.meta['organization_name'].unique().item(),
                device_name=atom_data.meta['device_name'].unique().item(),
                user_name=atom_data.meta['user_name'].unique().item(),
                datetime=atom_data.meta['datetime'].max(),
            ),
            levels=levels,
        )


@cache
def _parse_atom_data(
    __filepath: str,
    parser: AggregateByParallelsAtomDataParser,
) -> AtomData:

    xml = load_xml(__filepath)

    atom_data = parser.parse(
        __filepath,
        xml=xml,
    )
    return atom_data
