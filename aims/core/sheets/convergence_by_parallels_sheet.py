from dataclasses import dataclass

import numpy as np
import pandas as pd

from aims.config import Config
from aims.core.formatters import normalize_name
from aims.core.history import History
from aims.core.sheets.base_sheet import SheetABC
from aims.core.types import AnalysisName, Frame, ProbeName, Series
from aims.core.xml import AggregateByParallelsDataParser, parse_data
from aims.settings import FilterLevel


@dataclass
class ConvergenceByParallelsSheet(SheetABC):
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
    ) -> 'ConvergenceByParallelsSheet':
        """Get `sheet` from history."""

        queue = history.get_queue(
            analysis_name=analysis_name,
            n=5,
        )
        filepaths = history.get_filepaths(
            analysis_name=analysis_name,
            probe_name=probe_name,
        )

        if len(filepaths) == 0:
            raise ValueError('Sequence of filepaths is empty!')

        try:
            data_parser = AggregateByParallelsDataParser(config=config)

            meta = []
            reference = []
            prediction = []

            filepath = filepaths[-1]

            # parse
            meta, reference, prediction = parse_data(filepath, data_parser=data_parser)
            meta = pd.DataFrame(
                meta,
            ).reset_index(drop=True)
            reference = pd.DataFrame(
                reference,
            ).reset_index(drop=True)
            prediction = pd.DataFrame(
                prediction,
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

        #
        n_parallels = prediction.shape[0]
        values = pd.DataFrame(
            {},
            columns=nicknames,
        )
        for nickname in nicknames:
            values[nickname] = pd.to_numeric(prediction[nickname], errors='coerce')

        targets.loc['Cред.'] = values.mean(axis=0, skipna=True)
        targets.loc['СКО'] = values.std(axis=0, ddof=n_parallels > 1, skipna=True)
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
            prediction=prediction,
            targets=targets,
            levels=levels,
        )
