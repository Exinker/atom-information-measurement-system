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

                    for probe_id in probes.index:
                        if self.tracked_period.check(probes.loc[probe_id, 'datetime'], milestone=self.milestone):
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

    def _scrape_analysis(self, xml: XML) -> AnalysisName:
        """Parse analysis from given Atom's `xml`."""

        # scrape analysis
        try:
            analysis_name = xml.find('titul').find('aname').text

        except AttributeError:
            return ''

        return analysis_name

    def _scrape_probes(self, xml: XML) -> Frame:
        """Parse probes data from given Atom's `xml`."""
        probes = pd.DataFrame(
            columns=['id', 'name', 'datetime', 'is_certified'],
        ).set_index('id', drop=False)

        # scrape probe
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
