from datetime import datetime

import pandas as pd

from aims.config import Directory, TrackedPediod
from aims.core.formatters import normalize_datetime, normalize_name
from aims.core.types import AnalysisName, Frame, XML
from aims.core.xml.utils import (
    load_xml,
    validate_file,
    validate_xml,
    walk,
)


class Scraper:

    def __init__(
        self,
        milestone: datetime,
        directory: Directory,
        tracked_period: TrackedPediod,
        sep: str,
        verbose: bool = False,
    ) -> None:
        self.milestone = milestone
        self.directory = directory
        self.tracked_period = tracked_period
        self.sep = sep

        self.verbose = verbose

    def scrape(self) -> Frame:

        records = []
        for filepath in walk(self.directory):

            if validate_file(filepath, milestone=self.milestone, tracked_period=self.tracked_period):
                xml = load_xml(filepath)

                if validate_xml(xml):
                    analysis_name = self._scrape_analysis(xml)
                    probes = self._scrape_probes(xml)

                    for guid in probes.index:
                        is_tracked = self.tracked_period.check(probes.loc[guid, 'datetime'], milestone=self.milestone)
                        if is_tracked:
                            records.append({
                                'analysis_name': analysis_name,
                                'probe_name': probes.loc[guid, 'name'],
                                'probe_guid': probes.loc[guid, 'guid'],
                                'datetime': probes.loc[guid, 'datetime'],
                                'path': filepath,
                            })

        return pd.DataFrame(
            records,
            columns=['analysis_name', 'probe_name', 'probe_guid', 'datetime', 'path'],
        )

    def _scrape_analysis(self, xml: XML) -> AnalysisName:
        """Parse analysis from given Atom's `xml`."""

        try:
            analysis_name = xml.find('titul').find('aname').text
        except AttributeError:
            return ''
        else:
            return analysis_name

    def _scrape_probes(self, xml: XML) -> Frame:
        """Parse probes data from given Atom's `xml`."""
        default_probes = pd.DataFrame(
            columns=['guid', 'id', 'name', 'datetime', 'is_certified'],
        ).set_index('guid', drop=False)

        try:
            probes = default_probes.copy()
            for probe in xml.find('probes').findall('probe'):

                is_not_empty = len(probe.findall('spe')) > 0
                if is_not_empty:
                    try:
                        guid = probe.find('sample/guid').text
                    except AttributeError:
                        # FIXME: remove capability with old version XML files!
                        guid = probe.attrib['id']

                    probes.loc[guid, 'guid'] = guid
                    probes.loc[guid, 'id'] = int(probe.attrib['id'])
                    probes.loc[guid, 'name'] = normalize_name(probe.attrib['name'], sep=self.sep)
                    probes.loc[guid, 'datetime'] = normalize_datetime(probe.find('date[@type="last"]').text)
                    probes.loc[guid, 'is_certified'] = {
                        'yes': True,
                        'no': False,
                    }.get(probe.attrib.get('COC', 'no'))
        except AttributeError:
            return default_probes
        else:
            return probes
