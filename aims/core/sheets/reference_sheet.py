from dataclasses import dataclass

import numpy as np
import pandas as pd

from aims.config import Config
from aims.core.atom_database import MeasurementToleranceDatabase
from aims.core.formatters import normalize_name
from aims.core.history import History
from aims.core.sheets.base_sheet import SheetABC
from aims.core.types import AnalysisName, Frame, ProbeName, Series
from aims.core.xml import Parser, load_xml
from aims.settings import FilterLevel


@dataclass
class ReferenceSheet(SheetABC):
    analysis_name: AnalysisName
    probe_name: ProbeName
    meta: Frame
    prediction: Frame
    targets: Frame
    levels: Series

    @classmethod
    def from_history(
        cls,
        history: History,
        analysis_name: AnalysisName,
        probe_name: ProbeName,
        config: Config,
    ) -> 'ReferenceSheet':
        """Get `sheet` from history."""
        filepaths = history.get_paths(
            analysis_name=analysis_name,
            probe_name=probe_name,
        )

        if len(filepaths) == 0:
            raise ValueError('Sequence of filepaths is empty!')

        try:
            parser = Parser(config=config)

            meta = []
            reference = []
            prediction = []
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
                        name=_meta.iloc[j]['probe_name'],
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
                prediction.append(_prediction.drop(index=_meta.index[~cond]).reset_index(drop=True))

            meta = pd.DataFrame(
                pd.concat(meta),
            ).reset_index(drop=True)
            reference = pd.DataFrame(
                pd.concat(reference),
            ).reset_index(drop=True)
            prediction = pd.DataFrame(
                pd.concat(prediction),
            ).reset_index(drop=True)
        except (ValueError, KeyError):
            return cls.from_default(
                analysis_name=analysis_name,
                probe_name=probe_name,
            )

        # targets and levels
        nicknames = prediction.columns

        targets = pd.DataFrame(
            columns=nicknames,
        )
        levels = pd.DataFrame(
            columns=nicknames,
        )

        xml = load_xml(config.database_path)
        tolerance_database = MeasurementToleranceDatabase.from_xml(xml=xml, analysis_name=analysis_name)

        #
        n_probes = prediction.shape[0]
        values = pd.DataFrame(
            {},
            columns=nicknames,
        )
        for nickname in nicknames:
            values[nickname] = pd.to_numeric(prediction[nickname], errors='coerce')

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
            prediction=prediction,
            targets=targets,
            levels=levels,
        )
