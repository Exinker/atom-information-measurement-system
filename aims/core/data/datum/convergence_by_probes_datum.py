import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

from aims.config import Config
from aims.core.data.datum import DatumABC
from aims.core.history import ConvergenceByProbesHistory
from aims.core.parsers.parsers import (
    AggregateByProbesAtomDataParser,
    cache,
)
from aims.core.types import AnalysisName, Frame, ProbeName, Series
from aims.core.utils.formatters import normalize_name
from aims.core.utils.loaders import load_xml
from aims.settings import FilterLevel, SorterKind


@dataclass
class ConvergenceByProbesDatum(DatumABC):
    analysis_name: AnalysisName
    probe_name: ProbeName
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
            analysis_name=self.analysis_name,
            probe_name=self.probe_name,
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
            analysis_name=self.analysis_name,
            probe_name=self.probe_name,
            meta=self.meta,
            concentration=self.concentration[columns],
            targets=self.targets[columns],
            levels=self.levels[columns],
        )

    def select(self, columns: pd.Index) -> 'DatumABC':
        """Select from `sheet` by index."""
        cls = self.__class__

        return cls(
            analysis_name=self.analysis_name,
            probe_name=self.probe_name,
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
        probe_name: ProbeName,
        /,
        analysis_name: AnalysisName,
        history: ConvergenceByProbesHistory,
        config: Config,
    ) -> 'ConvergenceByProbesDatum':
        """Get `sheet` from history."""
        filepaths = history.get_filepaths(
            analysis_name=analysis_name,
            probe_name=probe_name,
        )

        if len(filepaths) == 0:
            raise ValueError('Sequence of filepaths is empty!')

        try:
            parser = AggregateByProbesAtomDataParser(config=config)

            meta = []
            reference = []
            concentration = []
            for filepath in filepaths:

                # parse
                _meta, _reference, _prediction = _parse_atom_data(filepath, parser=parser)

                # filtrate
                n_probes = _meta.shape[0]

                cond = np.full(n_probes, True)
                for j in range(n_probes):
                    pass

                    # check: probe's name
                    cond[j] = cond[j] and normalize_name(
                        name=_meta.iloc[j]['name'],
                        sep=history.sep,
                    ) == probe_name

                    # check: probe's created datetime
                    cond[j] = cond[j] and config.tracked_period.check(
                        _meta.iloc[j]['datetime'],
                        milestone=history.milestone,
                    )

                # drop and append
                meta.append(_meta.drop(index=_meta.index[~cond]).reset_index(drop=True))
                reference.append(_reference.drop(index=_meta.index[~cond]).reset_index(drop=True))
                concentration.append(_prediction.drop(index=_meta.index[~cond]).reset_index(drop=True))

            meta = pd.DataFrame(
                pd.concat(meta),
            ).reset_index(drop=True)
            reference = pd.DataFrame(
                pd.concat(reference),
            ).reset_index(drop=True)
            concentration = pd.DataFrame(
                pd.concat(concentration),
            ).reset_index(drop=True)
        except (ValueError, KeyError):
            return cls.from_default(
                analysis_name=analysis_name,
                probe_name=probe_name,
            )

        # targets and levels
        nicknames = concentration.columns

        targets = pd.DataFrame(
            columns=nicknames,
        )
        levels = pd.DataFrame(
            columns=nicknames,
        )

        #
        n_probes = concentration.shape[0]
        values = pd.DataFrame(
            {},
            columns=nicknames,
        )
        for nickname in nicknames:
            values[nickname] = pd.to_numeric(concentration[nickname], errors='coerce')

        targets.loc['Cред.'] = values.mean(axis=0, skipna=True)
        targets.loc['СКО'] = values.std(axis=0, ddof=n_probes > 1, skipna=True)
        targets.loc['ОСКО, %'] = 100 * targets.loc['СКО', nicknames] / targets.loc['Cред.', nicknames]

        values = targets.loc['ОСКО, %']
        levels = pd.Series(FilterLevel.NORMAL.value, index=values.index)
        levels[values.isna()] = FilterLevel.NOTSET.value
        levels[values >= 5] = FilterLevel.WARRING.value
        levels[values >= 10] = FilterLevel.DANGER.value

        return cls(
            analysis_name=analysis_name,
            probe_name=probe_name,
            meta=meta,
            concentration=concentration,
            targets=targets,
            levels=levels,
        )


@cache
def _parse_atom_data(
    __filepath: str,
    parser: AggregateByProbesAtomDataParser,
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
