import logging
from dataclasses import dataclass
from typing import ClassVar

import numpy as np
import pandas as pd

from aims.config import Config
from aims.managers.data_manager.atom_data import AtomData
from aims.managers.data_manager.cache import (
    CacheManager,
    cache,
)
from aims.managers.data_manager.data.datum import (
    DatumABC,
    DatumMeta,
    DatumSheet,
)
from aims.managers.data_manager.index import ConvergenceByProbesIndex
from aims.managers.data_manager.parsers import AggregateByProbesAtomDataParser
from aims.managers.data_manager.types import AnalysisName, ProbeName, Series
from aims.managers.data_manager.utils.formatters import normalize_name
from aims.managers.data_manager.utils.loaders import load_xml
from aims.settings import FilterLevel


LOGGER = logging.getLogger('app')


@dataclass
class ConvergenceByProbesDatum(DatumABC):
    sheet: DatumSheet
    meta: DatumMeta
    levels: Series

    META_COLUMN_NAMES: ClassVar = AggregateByProbesAtomDataParser.META_COLUMN_NAMES
    META_COLUMN_NAMES_VISIBLE: ClassVar = ['probe_name']
    TARGET_ROW_NAMES: ClassVar = [
        'Cред.',
        'СКО',
        'ОСКО, %',
    ]

    @classmethod
    def from_index(
        cls,
        probe_name: ProbeName,
        /,
        analysis_name: AnalysisName,
        index: ConvergenceByProbesIndex,
        config: Config,
    ) -> 'ConvergenceByProbesDatum':
        """Get `sheet` from index."""
        filepaths = index.get_filepaths(
            analysis_name=analysis_name,
            probe_name=probe_name,
        )

        if len(filepaths) == 0:
            raise ValueError('Sequence of filepaths is empty!')

        try:
            parser = AggregateByProbesAtomDataParser(config=config)

            meta = []
            concentration = []
            for filepath in filepaths:

                # parse
                atom_data = _process_atom_data(
                    filepath,
                    parser=parser,
                )

                # filtrate
                n_probes = atom_data.meta.shape[0]

                cond = np.full(n_probes, True)
                for j in range(n_probes):

                    # check: probe's name
                    cond[j] = cond[j] and normalize_name(
                        name=atom_data.meta.iloc[j]['probe_name'],
                        sep=index.sep,
                    ) == probe_name

                    # check: probe's created datetime
                    cond[j] = cond[j] and config.tracked_period.check(
                        atom_data.meta.iloc[j]['datetime'],
                        milestone=index.milestone,
                    )

                # drop and append
                meta.append(atom_data.meta.drop(index=atom_data.meta.index[~cond]).reset_index(drop=True))
                concentration.append(atom_data.concentration.drop(index=atom_data.meta.index[~cond]).reset_index(drop=True))  # noqa: E501

            meta = pd.DataFrame(
                pd.concat(meta),
            ).reset_index(drop=True)
            concentration = pd.DataFrame(
                pd.concat(concentration),
            ).reset_index(drop=True)
        except Exception as error:  # add custom exceptions
            LOGGER.warning('Atom data parse faild with %s: %s', type(error).__name__, error)
            return cls.from_default()

        # targets and levels
        n_probes = concentration.shape[0]
        nicknames = concentration.columns

        values = pd.DataFrame(
            {},
            columns=nicknames,
        )
        for nickname in nicknames:
            values[nickname] = pd.to_numeric(concentration[nickname], errors='coerce')
        targets = pd.DataFrame(
            columns=nicknames,
        )
        targets.loc['Cред.'] = values.mean(axis=0, skipna=True)
        targets.loc['СКО'] = values.std(axis=0, ddof=n_probes > 1, skipna=True)
        targets.loc['ОСКО, %'] = 100 * targets.loc['СКО', nicknames] / targets.loc['Cред.', nicknames]

        values = targets.loc['ОСКО, %']
        levels = pd.Series(FilterLevel.NORMAL.value, index=values.index)
        levels[values.isna()] = FilterLevel.NOTSET.value
        levels[values >= 5] = FilterLevel.WARRING.value
        levels[values >= 10] = FilterLevel.DANGER.value

        return cls(
            sheet=pd.concat([
                pd.concat([
                    meta,
                    concentration,
                ], axis=1),
                targets,
            ]),
            meta=DatumMeta(
                analysis_name=analysis_name,  # используется нормализованное имя анализа
                probe_name=probe_name,  # используется нормализованное имя пробы
                organization_name=atom_data.meta['organization_name'].unique().item(),
                device_name=atom_data.meta['device_name'].unique().item(),
                user_name=atom_data.meta['user_name'].unique().item(),
                datetime=meta['datetime'].max(),
            ),
            levels=levels,
        )


@cache(cache=CacheManager(field='parser'))
def _process_atom_data(
    __filepath: str,
    parser: AggregateByProbesAtomDataParser,
) -> AtomData:

    xml = load_xml(__filepath)

    atom_data = parser.parse(__filepath, xml=xml)
    return atom_data
