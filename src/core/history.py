
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator

import pandas as pd

from .config import DEBUG, TrackedPath
from .typing import AnalysisName, Frame, ProbeName, XML, XMLPath
from .utils import load_xml, normalize_datetime, normalize_name


def walk(path: TrackedPath) -> Iterator[tuple[XMLPath, XML]]:
    """Walk iterable along for a given path."""

    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:

            if filename.endswith('.xml'):
                filepath = os.path.join(dirpath, filename)
                xml = load_xml(filepath)

                if xml is not None:
                    yield filepath, xml


def parse_analysis(xml: XML) -> AnalysisName:
    """Parse analysis from given Atom's `xml`."""
    # TODO: have to check atom's xml!

    analysis_name = ''

    try:
        analysis_name = xml.find('titul').find('aname').text

    except AttributeError:
        return ''

    return analysis_name


def parse_probes(xml: XML, sep: str) -> Frame:
    """Parse probes data from given Atom's `xml`."""
    # TODO: have to check atom's xml!

    probes = pd.DataFrame(
        columns=['id', 'name', 'dt'],
    ).set_index('id', drop=False)

    # parse probe
    try:
        for probe in xml.find('probes').findall('probe'):

            is_not_empty = len(probe.findall('spe')) > 0
            if is_not_empty:
                probe_id = int(probe.attrib['id'])
                probes.loc[probe_id, 'id'] = probe_id
                probes.loc[probe_id, 'name'] = normalize_name(probe.attrib['name'], sep=sep)
                probes.loc[probe_id, 'dt'] = normalize_datetime(probe.find('date[@type="last"]').text)

    except AttributeError:
        return None

    return probes


# --------        History        --------
@dataclass
class Record:
    analysis_name: AnalysisName = field(default='')
    probe_name: ProbeName = field(default='')
    dt: datetime = field(default_factory=lambda: datetime.fromtimestamp(0))


@dataclass
class History:
    records: Frame
    tracked_path: TrackedPath
    sep: str

    @property
    def last_analisys_name(self) -> AnalysisName:
        """Get the last `Record`'s analysis name."""

        # select data
        data = self.records[['analysis_name', 'dt']].copy(deep=True)
        data = data.set_index('dt', drop=False)
        data = data.sort_index()

        #
        if data.empty:
            return ''

        datum = data.iloc[-1]
        return datum['analysis_name']

    @property
    def last_record(self) -> Record:
        """Get the last `Record`."""

        # select data
        data = self.records[['analysis_name', 'probe_name', 'dt']].copy(deep=True)
        data = data.set_index('dt', drop=False)
        data = data.sort_index()

        #
        if data.empty:
            return Record()

        record = Record(**data.iloc[-1])
        return record

    def add(self) -> None:
        raise NotImplementedError

    def get_queue(self, analysis_name: AnalysisName, n: int = 1, ascending: bool = False) -> tuple[ProbeName]:
        """Get the `n` latest probe names for a given `analysis_name`."""

        # select from records
        cond = (self.records['analysis_name'] == analysis_name)
        data = self.records[cond][['probe_name', 'dt']].copy(deep=True)
        data = data.set_index('dt', drop=False)
        data = data.groupby(by='probe_name').max().sort_values(by='dt')

        if data.empty:
            return tuple()

        #
        probe_names = tuple(data.iloc[-n:].index)
        probe_names = probe_names if ascending else reversed(probe_names)
        return probe_names

    def get_index(self, analysis_name: AnalysisName, probe_name: ProbeName) -> tuple[XMLPath]:
        """Get filepaths of all `xml` files for a given analysis and probe's name."""

        # select from records
        cond = (self.records['analysis_name'] == analysis_name) & (self.records['probe_name'] == probe_name)
        data = self.records[cond][['analysis_name', 'probe_name', 'path']].copy(deep=True)

        #
        if data.empty:
            return tuple()

        paths = tuple(data['path'].unique())
        return paths

    # --------        handlers        --------
    @classmethod
    def from_path(cls, tracked_path: TrackedPath, sep: str, verbose: bool = False) -> 'History':
        """Get history for a given path by iterable walk."""

        records = []
        for filepath, xml in walk(tracked_path):
            if verbose or DEBUG:
                print(filepath)

            # parse analysis data
            analysis_name = parse_analysis(xml)
            if analysis_name == '':
                continue

            # parse probe data
            probes = parse_probes(xml, sep=sep)
            if verbose or DEBUG:
                print(probes)

            if probes.empty:
                continue

            #
            for probe_id in probes.index:
                records.append({
                    'analysis_name': analysis_name,
                    'probe_name': probes.loc[probe_id, 'name'],
                    'dt': probes.loc[probe_id, 'dt'],
                    'path': filepath,
                })

        records = pd.DataFrame(
            records,
            columns=['analysis_name', 'probe_name', 'dt', 'path'],
        )

        #
        return cls(
            records=records,
            tracked_path=tracked_path,
            sep=sep,
        )
