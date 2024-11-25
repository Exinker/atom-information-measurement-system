from datetime import datetime
from typing import Any, Mapping

import pandas as pd

from aims.config import Directory, TrackedPediod
from aims.core.parsers import (
    ParserCache,
    cache,
)
from aims.core.scrapers.utils import (
    validate_file,
    validate_xml,
    walk,
)
from aims.core.types import AnalysisName, Frame, XML
from aims.core.utils.formatters import (
    normalize_datetime,
    normalize_name,
)
from aims.core.utils.loaders import load_xml


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
            record = _scrape_xml(
                filepath,
                milestone=self.milestone,
                tracked_period=self.tracked_period,
                sep=self.sep,
            )
            if record is not None:
                records.append(record)

        return pd.DataFrame(
            records,
            columns=['analysis_name', 'probe_name', 'probe_guid', 'datetime', 'path'],
        )


@cache(cache=ParserCache(method='scrape'))
def _scrape_xml(
    __filepath: str,
    milestone: datetime,
    tracked_period: TrackedPediod,
    sep: str,
) -> Mapping[str, Any]:

    if validate_file(
        __filepath,
        milestone=milestone,
        tracked_period=tracked_period,
    ):
        xml = load_xml(__filepath)

        if validate_xml(xml):
            analysis_name = _scrape_analysis(xml)
            probes = _scrape_probes(xml, sep=sep)

            for probe_guid in probes.index:
                is_tracked = tracked_period.check(probes.loc[probe_guid, 'datetime'], milestone=milestone)
                if is_tracked:
                    return {
                        'analysis_name': analysis_name,
                        'probe_name': probes.loc[probe_guid, 'name'],
                        'probe_guid': probes.loc[probe_guid, 'probe_guid'],
                        'datetime': probes.loc[probe_guid, 'datetime'],
                        'path': __filepath,
                    }

    return None


def _scrape_analysis(xml: XML) -> AnalysisName:
    """Parse analysis from given Atom's `xml`."""

    try:
        analysis_name = xml.find('titul').find('aname').text
    except AttributeError:
        return ''
    else:
        return analysis_name


def _scrape_probes(
    xml: XML,
    sep: str,
) -> Frame:
    """Parse probes data from given Atom's `xml`."""
    default_probes = pd.DataFrame(
        columns=['probe_guid', 'id', 'name', 'datetime', 'is_certified'],
    ).set_index('probe_guid', drop=False)

    try:
        probes = default_probes.copy()
        for probe in xml.find('probes').findall('probe'):

            is_not_empty = len(probe.findall('spe')) > 0
            if is_not_empty:
                try:
                    probe_guid = probe.find('sample/guid').text
                except AttributeError:
                    # FIXME: remove capability with old version XML files!
                    probe_guid = probe.attrib['id']

                probes.loc[probe_guid, 'probe_guid'] = probe_guid
                probes.loc[probe_guid, 'id'] = int(probe.attrib['id'])
                probes.loc[probe_guid, 'name'] = normalize_name(probe.attrib['name'], sep=sep)
                probes.loc[probe_guid, 'datetime'] = normalize_datetime(probe.find('date[@type="last"]').text)
                probes.loc[probe_guid, 'is_certified'] = {
                    'yes': True,
                    'no': False,
                }.get(probe.attrib.get('COC', 'no'))
    except AttributeError:
        return default_probes
    else:
        return probes
