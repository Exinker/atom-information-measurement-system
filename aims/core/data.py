import os
import time
from dataclasses import dataclass
from datetime import datetime

from functools import partial
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd

from aims.config import Config, TrackedMode
from aims.settings import FilterLevel, SorterKind

from .atom_database import MeasurementToleranceDatabase
from .history import History
from .scraper import load_xml
from .types import AnalysisName, Frame, ProbeName, Series
from .utils import normalize_name
from .xml import Parser


@dataclass
class Datum:
    analysis_name: AnalysisName
    probe_name: ProbeName
    meta: Frame
    prediction: Frame
    targets: Frame
    levels: Series

    @property
    def last_meta(self) -> Series | None:  # TODO: return Probe dataclass!
        """Get the last recorded probe's meta `Series`."""

        data = self.meta.copy(deep=True)
        data = data.set_index('datetime', drop=False)
        data = data.sort_index()

        #
        if data.empty:
            return None

        return data.iloc[-1]

    # --------        handlers        --------
    def filtrate(self, level: FilterLevel) -> 'Datum':
        """Filtrate `datum` by selected level."""
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

    def sort(self, kind: SorterKind) -> 'Datum':
        """Sort `datum` by selected kind."""
        cls = self.__class__

        match kind:
            case SorterKind.NONE:
                columns = self.targets.columns
            case SorterKind.FILTER:
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

    def to_frame(self) -> Frame:
        return pd.concat([pd.concat([self.meta, self.prediction], axis=1), self.targets])

    # --------        factory        --------
    @classmethod
    def from_default(cls, analysis_name: AnalysisName = '', probe_name: ProbeName = '') -> 'Datum':
        """Get empty `datum`."""

        return cls(
            analysis_name=analysis_name,
            probe_name=probe_name,
            meta=pd.DataFrame({}, columns=['file_dir', 'file_name', 'datetime', 'analysis_name', 'organization_name', 'device_name', 'user_name', 'probe_name', 'is_certified']),
            prediction=pd.DataFrame(),
            targets=pd.DataFrame(),
            levels=pd.Series(),
        )

    @classmethod
    def from_history(cls, history: History, analysis_name: AnalysisName, probe_name: ProbeName, config: Config) -> 'Datum':
        """Get `datum` from history."""

        #
        filepaths = history.get_paths(
            analysis_name=analysis_name,
            probe_name=probe_name,
        )

        if len(filepaths) == 0:
            raise ValueError('List of filepaths is empty!')

        try:
            parser = Parser(config=config)
            items = [parser.parse(filepath, analysis_name=analysis_name, probe_name=probe_name) for filepath in filepaths]

            meta = pd.DataFrame(
                pd.concat([meta for meta, reference, prediction in items]),
            ).reset_index(drop=True)
            reference = pd.DataFrame(
                pd.concat([reference for meta, reference, prediction in items]),
            ).reset_index(drop=True)
            prediction = pd.DataFrame(
                pd.concat([prediction for meta, reference, prediction in items]),
            ).reset_index(drop=True)

        except (ValueError, KeyError):
            # TODO: add logging

            return Datum.from_default(
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
        match config.tracked_mode:

            case TrackedMode.CONVERGENCE:
                n_probes = prediction.shape[0]
                values = pd.DataFrame(
                    {},
                    columns=nicknames,
                )
                for nickname in nicknames:
                    values[nickname] = pd.to_numeric(prediction[nickname], errors='coerce')

                #
                targets.loc['Cред.'] = values.mean(axis=0, skipna=True)
                targets.loc['СКО'] = values.std(axis=0, ddof=n_probes > 1, skipna=True)
                targets.loc['ОСКО, %'] = 100 * targets.loc['СКО', nicknames] / targets.loc['Cред.', nicknames]

                values = targets.loc['ОСКО, %']
                levels = pd.Series(FilterLevel.NORMAL.value, index=values.index)
                levels[values.isna()] = FilterLevel.NOTSET.value
                levels[values >= 5] = FilterLevel.WARRING.value
                levels[values >= 10] = FilterLevel.DANGER.value

            case TrackedMode.REFERENCE:
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

                #
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

                #
                print()

            case TrackedMode.NONE:
                pass

            case _:
                raise ValueError(f'mode {config.tracked_mode} is not supported!')

        #
        return cls(
            analysis_name=analysis_name,
            probe_name=probe_name,
            meta=meta,
            prediction=prediction,
            targets=targets,
            levels=levels,
        )


@dataclass
class Data:
    items: tuple[Datum]

    @property
    def last_datum(self) -> Datum | None:
        """Get the last recorded `datum`."""
        try:
            return self.items[0]

        except IndexError:
            return Datum.from_default()

    # --------        factory        --------
    @classmethod
    def from_history(cls, history: History, config: Config) -> 'Data':

        # tracked analysis
        tracked_analysis_name = config.tracked_analisys_name or history.last_analisys_name

        # tracked probes
        if config.tracked_probe_name:
            tracked_probe_names = (config.tracked_probe_name, ) + history.get_queue(analysis_name=tracked_analysis_name, n=config.tracked_queue_length - 1)
        else:
            tracked_probe_names = history.get_queue(analysis_name=tracked_analysis_name, n=config.tracked_queue_length)

        #
        print(f'cpu count: {cpu_count()}')
        with Pool() as pool:
            target = partial(Datum.from_history, history, tracked_analysis_name, config=config)
            items = pool.map(target, tracked_probe_names)

        # items = []
        # for tracked_probe_name in tracked_probe_names:
        #     item = Datum.from_history(
        #         history=history,
        #         analysis_name=tracked_analysis_name,
        #         probe_name=tracked_probe_name,
        #         config=config,
        #     )
        #     items.append(item)

        #
        return cls(
            items=tuple(items),
        )

    # --------        private        --------
    def __getitem__(self, i: int) -> Datum:
        return self.items[i]


# --------        factory        --------
def fetch_data(milestone: datetime, config: Config) -> Data:

    # history
    history = History.from_path(
        milestone=milestone,
        directory=config.directory,
        tracked_period=config.tracked_period,
        sep=config.sep,
    )

    #  data
    data = Data.from_history(
        history=history,
        config=config,
    )

    return data
