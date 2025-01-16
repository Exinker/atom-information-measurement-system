import logging
from datetime import datetime
from typing import Any, Iterable, Mapping

import pandas as pd

from aims.config import TrackedPediod
from aims.managers.data_manager.cache import (
    CacheManager,
    cache,
)
from aims.managers.data_manager.scrapers.utils.validators import (
    validate_file,
    validate_xml,
)
from aims.managers.data_manager.types import (
    AnalysisName,
    Frame,
    XML,
)
from aims.managers.data_manager.utils.formatters import (
    normalize_datetime,
    normalize_name,
)
from aims.managers.data_manager.utils.loaders import load_xml


LOGGER = logging.getLogger('app')
DEFAULT_PROBES = pd.DataFrame(
    columns=['probe_guid', 'id', 'name', 'datetime', 'is_certified'],
).set_index('probe_guid', drop=False)


@cache(cache=CacheManager(field='scraper'))
def scrape_xml(
    __filepath: str,
    milestone: datetime,
    tracked_period: TrackedPediod,
    sep: str,
) -> Iterable[Mapping[str, Any]]:

    is_validated = validate_file(__filepath, milestone=milestone, tracked_period=tracked_period)
    if is_validated:
        xml = load_xml(__filepath)

        if xml is None:
            return []

        is_validated = validate_xml(xml)
        if is_validated:
            analysis_name = scrape_analysis_name(xml)
            probes = scrape_probes(xml, sep=sep)

            records = []
            for probe_guid in probes.index:
                is_tracked = tracked_period.check(probes.loc[probe_guid, 'datetime'], milestone=milestone)
                if is_tracked:
                    record = {
                        'analysis_name': analysis_name,
                        'probe_name': probes.loc[probe_guid, 'name'],
                        'probe_guid': probes.loc[probe_guid, 'probe_guid'],
                        'datetime': probes.loc[probe_guid, 'datetime'],
                        'path': __filepath,
                    }
                    records.append(record)
            return records

        else:
            LOGGER.warning('XML %s is not validated!', __filepath)

    return []


def scrape_analysis_name(xml: XML) -> AnalysisName:
    """Parse analysis from given Atom's `xml`."""

    try:
        analysis_name = xml.find('titul/aname').text or ''
    except AttributeError:
        analysis_name = ''

    return analysis_name


def scrape_probes(
    __xml: XML,
    sep: str,
) -> Frame:
    """Parse probes data from given Atom's `xml`."""

    probes = DEFAULT_PROBES.copy()
    try:
        for probe in __xml.find('probes').findall('probe'):  # TODO: xpath

            is_not_empty = len(probe.findall('spe')) > 0
            if is_not_empty:

                try:
                    probe_guid = probe.find('sample/guid').text
                except AttributeError:  # FIXME: remove capability with old version XML files!
                    probe_guid = probe.attrib['id']

                probes.loc[probe_guid, 'probe_guid'] = probe_guid
                probes.loc[probe_guid, 'id'] = int(probe.attrib['id'])
                probes.loc[probe_guid, 'name'] = normalize_name(
                    name=probe.attrib['name'],
                    sep=sep,
                )
                probes.loc[probe_guid, 'created_at'] = normalize_datetime(
                    created_at=probe.find('date[@type="last"]').text,
                )
                probes.loc[probe_guid, 'is_certified'] = {
                    'yes': True,
                    'no': False,
                }.get(probe.attrib.get('COC', 'no'))

    except AttributeError:
        return DEFAULT_PROBES.copy()
    else:
        return probes
