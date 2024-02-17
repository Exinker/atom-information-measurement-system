
import os
from dataclasses import dataclass
from datetime import timedelta

import numpy as np
import pandas as pd

from .alias import AnalysisName, Frame, ProbeName, Series
from .atom_data import AtomData
from .atom_database import MeasurementToleranceDatabase
from .config import Config, TrackedPediod, Mode
from .history import History
from .utils import load_xml, normalize_name
from .setting import FilterLevel, SorterKind


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
        data = data.set_index('datetime_created', drop=False)
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

    @classmethod
    def from_default(cls, analysis_name: AnalysisName = '', probe_name: ProbeName = '',) -> 'Datum':
        """Get empty `datum`."""

        return cls(
            analysis_name=analysis_name,
            probe_name=probe_name,
            meta=pd.DataFrame({}, columns=['file_dir', 'file_name', 'datetime_created', 'analysis_name', 'organization_name', 'device_name', 'user_name', 'probe_name', 'is_certified']),
            prediction=pd.DataFrame(),
            targets=pd.DataFrame(),
            levels=pd.Series(),
        )

    @classmethod
    def from_history(cls, tracked_analysis: AnalysisName, tracked_probe: ProbeName, history: History, config: Config) -> 'Datum':
        """Get `datum` from history."""

        # last record
        cond = (history.records['analysis_name'] == tracked_analysis) & ((history.records['probe_name'] == tracked_probe))
        records = history.records[cond]

        last_record = records.iloc[-1]

        #
        try:
            # meta, prediction, reference
            index = history.get_index(analysis_name=tracked_analysis, probe_name=tracked_probe)
            if len(index) == 0:
                raise ValueError('List of paths is empty!')

            meta = []
            reference = []
            prediction = []
            i = -1
            for path in index:
                filedir, filename = os.path.split(path)

                xml = load_xml(path)

                # atom data
                atom_data = AtomData.from_xml(
                    xml=xml,
                    filtrated_by_sheet=config.filtrated_by_sheet,
                    filtrated_by_label=config.filtrated_by_label,
                )

                # filtrate probes
                probes = atom_data.probes
                n_probes, _ = probes.shape

                cond = np.full((n_probes, ), True)
                for j in range(n_probes):

                    # check: probe's name
                    if normalize_name(probes.iloc[j]['name'], history.sep) != tracked_probe:
                        cond[j] = False

                    # check: probe's created datetime
                    match config.tracked_period:
                        case TrackedPediod.ALL:
                            pass

                        case TrackedPediod.DAY:
                            if probes.iloc[j]['datetime_created'].date() != last_record['dt'].date():
                                cond[j] = False

                        case TrackedPediod._24H:
                            if pd.to_datetime(probes.iloc[j]['datetime_created']) < (last_record['dt'] - timedelta(days=1)):
                                cond[j] = False

                        case _:
                            assert False, f'Tracked pediod {config.tracked_period} is not used!.'

                # parse probes
                for probe_id in atom_data.probes.index[cond]:
                    i += 1

                    meta.append({
                        'i': i,
                        'file_dir': filedir,
                        'file_name': filename,
                        'datetime_created': atom_data.probes.loc[probe_id, 'datetime_created'],
                        'analysis_name': atom_data.meta.analysis_name,
                        'organization_name': atom_data.meta.organization_name,
                        'device_name': atom_data.meta.device_name,
                        'user_name': atom_data.meta.user_name,
                        'probe_name': atom_data.probes.loc[probe_id, 'name'],
                        'is_certified': atom_data.probes.loc[probe_id, 'is_certified'],
                    })

                    reference.append(dict(
                        **{'i': i},
                        **{
                            symbol: value
                            for symbol, value in atom_data.reference.loc[probe_id].to_dict().items()
                        },
                    ))

                    prediction.append(dict(
                        **{'i': i},
                        **{
                            atom_data.lines.loc[line_id, 'symbol'] + ' ' + str(atom_data.lines.loc[line_id, 'wavelength']): values
                            for line_id, values in atom_data.prediction.loc[probe_id].to_dict().items()
                        },
                    ))

            meta = pd.DataFrame(
                meta,
            ).set_index(['i'], drop=True)
            reference = pd.DataFrame(
                reference,
            ).set_index(['i'], drop=True).iloc[-1]
            prediction = pd.DataFrame(
                prediction,
            ).set_index(['i'], drop=True)

        except (ValueError, KeyError):
            # TODO: add logging

            return Datum.from_default(
                analysis_name=tracked_analysis,
                probe_name=tracked_probe,
            )

        # targets and levels
        nicknames = prediction.columns

        targets = pd.DataFrame(
            columns=nicknames,
        )
        levels = pd.DataFrame(
            columns=nicknames,
        )
        match config.mode:

            case Mode.CONVERGENCE:
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

            case Mode.REFERENCE:
                xml = load_xml(config.database_path)
                tolerance_database = MeasurementToleranceDatabase.from_xml(xml=xml, analysis_name=tracked_analysis)

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

            case Mode.NONE:
                pass

            case _:
                raise ValueError(f'mode {config.mode} is not supported!')

        #
        return cls(
            analysis_name=tracked_analysis,
            probe_name=tracked_probe,
            meta=meta,
            prediction=prediction,
            targets=targets,
            levels=levels,
        )

    def to_frame(self) -> Frame:
        return pd.concat([pd.concat([self.meta, self.prediction], axis=1), self.targets])


@dataclass
class Data:
    items: tuple[Datum]

    def __getitem__(self, i: int) -> Datum:
        return self.items[i]

    @property
    def last_datum(self) -> Datum | None:
        """Get the last recorded `datum`."""
        try:
            return self.items[0]

        except IndexError:
            return None

    # --------        handlers        --------
    @classmethod
    def from_history(cls, history: History, config: Config) -> 'Data':

        # tracked analysis
        tracked_analysis = config.tracked_analisys or history.last_analisys_name

        # tracked probes
        if config.tracked_probe:
            tracked_probes = (config.tracked_probe, ) + history.get_queue(analysis_name=tracked_analysis, n=config.tracked_queue - 1)
        else:
            tracked_probes = history.get_queue(analysis_name=tracked_analysis, n=config.tracked_queue)

        #
        items = []
        for tracked_probe in tracked_probes:
            item = Datum.from_history(
                tracked_analysis=tracked_analysis,
                tracked_probe=tracked_probe,
                history=history,
                config=config,
            )
            items.append(item)

        #
        return cls(
            items=tuple(items),
        )


def fetch_data(config: Config) -> Data:

    # history
    history = History.from_path(tracked_path=config.tracked_path, sep=config.sep)
    print(history)

    #  data
    data = Data.from_history(
        history=history,
        config=config,
    )

    return data
