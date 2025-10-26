from dataclasses import dataclass

import numpy as np
import pandas as pd

from aims.configs import Config
from aims.managers.data_manager.atom_database import MeasurementToleranceDatabase
from aims.managers.data_manager.data.datum import DatumABC
from aims.managers.data_manager.index import IndexABC
from aims.managers.data_manager.parsers import AggregateByProbesAtomDataParser
from aims.managers.data_manager.types import AnalysisName, Frame, ProbeName, Series
from aims.managers.data_manager.utils.formatters import normalize_name
from aims.managers.data_manager.utils.loaders import load_xml
from aims.settings import FilterLevel


@dataclass
class ReferenceSheet(DatumABC):
    analysis_name: AnalysisName
    probe_name: ProbeName
    meta: Frame
    concentration: Frame
    targets: Frame
    levels: Series

    @classmethod
    def from_index(
        cls,
        index: IndexABC,
        analysis_name: AnalysisName,
        probe_name: ProbeName,
        config: Config,
    ) -> 'ReferenceSheet':
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
            reference = []
            concentration = []
            for filepath in filepaths:

                # parse
                _meta, _reference, _prediction = parser.parse(filepath)

                # filtrate
                n_probes = _meta.shape[0]

                cond = np.full(n_probes, True)
                for j in range(n_probes):
                    pass

                    # check: probe's name
                    cond[j] = cond[j] and normalize_name(
                        name=_meta.iloc[j]['name'],
                        sep=index.sep,
                    ) == probe_name

                    # check: probe's created datetime
                    cond[j] = cond[j] and config.tracked_period.check(
                        _meta.iloc[j]['datetime'],
                        milestone=index.milestone,
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

        xml = load_xml(config.database_path)
        tolerance_database = MeasurementToleranceDatabase.create(xml=xml, analysis_name=analysis_name)

        #
        n_probes = concentration.shape[0]
        values = pd.DataFrame(
            {},
            columns=nicknames,
        )
        for nickname in nicknames:
            values[nickname] = pd.to_numeric(concentration[nickname], errors='coerce')

        targets.loc['Cред.'] = values.mean(axis=0, skipna=True)
        targets.loc['Аттест.'] = []  # FIXME:

        values = targets.loc['Cред.']
        levels = pd.Series(FilterLevel.NORMAL.value, index=values.index)
        for column in values.index:
            symbol, _ = column.split(' ', maxsplit=1)

            tol = tolerance_database.get_tolerance(symbol=symbol, conc=targets.loc['Cред.', column])

            if tol is None:
                levels[column] = FilterLevel.NOTSET.value
            else:
                print()

        return cls(
            analysis_name=analysis_name,
            probe_name=probe_name,
            meta=meta,
            concentration=concentration,
            targets=targets,
            levels=levels,
        )
