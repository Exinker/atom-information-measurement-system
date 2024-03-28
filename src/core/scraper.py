import os
import xml.etree.ElementTree as ElementTree
from datetime import datetime
from typing import Iterator

import pandas as pd

from src.config import TrackedPath, TrackedPediod

from .typing import AnalysisName, Frame, XML, XMLPath
from .utils import normalize_datetime, normalize_name


# --------        file        --------
def walk(tracked_path: TrackedPath) -> Iterator[XMLPath]:
    """Walk iterable along for a given path."""

    for filedir, _, filenames in os.walk(tracked_path):
        for filename in filenames:
            filepath = os.path.join(filedir, filename)

            yield filepath


def validate_file(filepath: XMLPath, tracked_period: TrackedPediod) -> bool:
    """Validate file to the simplest cases."""

    # validate file's extension
    if not filepath.endswith('.xml'):
        return False

    # validate file's created datetime
    filestat = os.stat(filepath)

    created_at = datetime.fromtimestamp(filestat.st_ctime)
    if not tracked_period.check(created_at):
        return False

    #
    return True


# --------        xml        --------
def load_xml(filepath: XMLPath) -> XML | None:
    """Load `xml` element object from file for a given `filepath`."""

    try:
        tree = ElementTree.parse(filepath)
        xml = tree.getroot()

        return xml

    except Exception:
        return None


def validate_xml(xml: XML | None) -> bool:
    """Validate `xml` to simplest cases."""

    if xml is None:
        return False

    # check analysis
    if xml.tag != 'analysis':
        return False

    # check titul
    titul = xml.find('titul')
    if titul is None:
        return False

    if any(titul.find(tag) is None for tag in ('organization', 'device', 'user', 'date', 'aname')):
        return False

    # check probes
    probes = xml.find('probes')
    if probes is None:
        return False

    # check columns
    columns = xml.find('columns')
    if columns is None:
        return False

    #
    return True


# --------        scraper        --------
class Scraper:

    def __init__(self, tracked_path: TrackedPath, tracked_period: TrackedPediod, sep: str, verbose: bool = False):
        self.tracked_path = tracked_path
        self.tracked_period = tracked_period
        self.sep = sep

        self.verbose = verbose

    def parse(self) -> Frame:

        records = []
        for filepath in walk(self.tracked_path):

            if validate_file(filepath, tracked_period=self.tracked_period):

                xml = load_xml(filepath)
                if validate_xml(xml):
                    analysis_name = self._parse_analysis(xml)
                    probes = self._parse_probes(xml)

                    for probe_id in probes.index:
                        records.append({
                            'analysis_name': analysis_name,
                            'probe_name': probes.loc[probe_id, 'name'],
                            'datetime': probes.loc[probe_id, 'datetime'],
                            'path': filepath,
                        })

        return pd.DataFrame(
            records,
            columns=['analysis_name', 'probe_name', 'datetime', 'path'],
        )

    # --------        private        --------
    def _parse_analysis(self, xml: XML) -> AnalysisName:
        """Parse analysis from given Atom's `xml`."""

        # parse analysis
        try:
            analysis_name = xml.find('titul').find('aname').text

        except AttributeError:
            return ''

        return analysis_name

    def _parse_probes(self, xml: XML) -> Frame:
        """Parse probes data from given Atom's `xml`."""
        probes = pd.DataFrame(
            columns=['id', 'name', 'datetime', 'is_certified'],
        ).set_index('id', drop=False)

        # parse probe
        try:
            for probe in xml.find('probes').findall('probe'):

                is_not_empty = len(probe.findall('spe')) > 0
                if is_not_empty:
                    probe_id = int(probe.attrib['id'])

                    probes.loc[probe_id, 'id'] = probe_id
                    probes.loc[probe_id, 'name'] = normalize_name(probe.attrib['name'], sep=self.sep)
                    probes.loc[probe_id, 'datetime'] = normalize_datetime(probe.find('date[@type="last"]').text)
                    probes.loc[probe_id, 'is_certified'] = {
                        'yes': True,
                        'no': False,
                    }.get(probe.attrib.get('COC', 'no'))

        except AttributeError:
            return pd.DataFrame(
                columns=['id', 'name', 'datetime'],
            ).set_index('id', drop=False)

        return probes
