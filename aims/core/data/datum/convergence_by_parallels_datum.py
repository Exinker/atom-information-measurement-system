import logging
from dataclasses import dataclass
from typing import ClassVar

import numpy as np
import pandas as pd

from aims.config import Config
from aims.core.atom_data import AtomData
from aims.core.cache import (
    CacheManager,
    cache,
)
from aims.core.data.datum import (
    DatumABC,
    DatumMeta,
    DatumSheet,
)
from aims.core.index import ConvergenceByParallelsIndex
from aims.core.parsers import AggregateByParallelsAtomDataParser
from aims.core.types import ProbeGUID, Series
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
    def from_index(
        cls,
        probe_guid: ProbeGUID,
        /,
        index: ConvergenceByParallelsIndex,
        config: Config,
    ) -> 'ConvergenceByParallelsDatum':
        """Get `sheet` from index."""
        filepath = index.get_filepath(
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
                    milestone=index.milestone,
                )
        except Exception as error:  # add custom exceptions
            LOGGER.warning('Atom data parse faild with %s: %s', type(error).__name__, error)
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


@cache(cache=CacheManager(field='parser'))
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
