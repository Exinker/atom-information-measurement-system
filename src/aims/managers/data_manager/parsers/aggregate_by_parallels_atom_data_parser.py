import logging
from warnings import simplefilter

import pandas as pd

from aims.config import Config, FiltratedLabel, FiltratedSheet
from aims.managers.data_manager.atom_data import AtomData
from aims.managers.data_manager.parsers.base_atom_data_parser import AtomDataParserABC
from aims.managers.data_manager.parsers.utils import (
    find_columns,
    find_sheets,
    parse_column,
)
from aims.managers.data_manager.types import XML, XMLPath
from aims.managers.data_manager.utils.formatters import normalize_datetime


simplefilter(action="ignore", category=pd.errors.PerformanceWarning)  # TODO


LOGGER = logging.getLogger('app')


class AggregateByParallelsAtomDataParser(AtomDataParserABC):

    META_COLUMN_NAMES = [
        'filepath',
        'organization_name',
        'device_name',
        'user_name',
        'analysis_name',
        'probe_guid',
        'probe_id',
        'probe_name',
        'datetime',
        'is_certified',
        'parallel_id',
        'parallel_name',
    ]

    def __init__(self, config: Config):
        super().__init__(config=config)

    def parse(
        self,
        __filepath: XMLPath,
        xml: XML,
    ) -> AtomData:
        """Get recorded data from Atom's .xml file."""

        LOGGER.debug('Parse XML file: %r', __filepath)
        try:
            data = self._parse(
                xml=xml,
                filepath=__filepath,
                filtrated_by_sheet=self.config.filtrated_by_sheet,
                filtrated_by_label=self.config.filtrated_by_label,
            )
        except Exception as error:
            LOGGER.warning('XML parse failed with %s: %s', type(error).__name__, error)
            raise
        else:
            return data

    @classmethod
    def _parse(
        cls,
        xml: XML,
        filepath: XMLPath,
        filtrated_by_sheet: FiltratedSheet,
        filtrated_by_label: FiltratedLabel,
    ) -> AtomData:
        """Get recorded data from Atom's .xml file."""

        organization_name = xml.find('titul').find('organization').text
        device_name = xml.find('titul').find('device').text
        user_name = xml.find('titul').find('user').text
        analysis_name = xml.find('titul').find('aname').text

        meta = pd.DataFrame(
            columns=cls.META_COLUMN_NAMES,
        ).set_index('parallel_id', drop=False)
        for probe in xml.find('probes').findall('probe'):

            is_not_empty = len(probe.findall('spe')) > 0
            if is_not_empty:
                probe_guid = probe.find('sample/guid').text
                probe_name = probe.attrib.get('name', '???')
                is_certified = {
                    'yes': True,
                    'no': False,
                }.get(probe.attrib.get('COC', 'no'))

                for parallel in probe.findall('spe'):
                    parallel_id = int(parallel.attrib['id'])

                    meta.loc[parallel_id, 'filepath'] = filepath
                    meta.loc[parallel_id, 'organization_name'] = organization_name
                    meta.loc[parallel_id, 'device_name'] = device_name
                    meta.loc[parallel_id, 'user_name'] = user_name
                    meta.loc[parallel_id, 'analysis_name'] = analysis_name
                    meta.loc[parallel_id, 'probe_guid'] = probe_guid
                    meta.loc[parallel_id, 'probe_id'] = int(probe.attrib['id'])
                    meta.loc[parallel_id, 'probe_name'] = probe_name
                    meta.loc[parallel_id, 'datetime'] = normalize_datetime(parallel.find('date').text)
                    meta.loc[parallel_id, 'is_certified'] = is_certified
                    meta.loc[parallel_id, 'parallel_id'] = parallel_id
                    meta.loc[parallel_id, 'parallel_name'] = parallel.attrib.get('name', '???')

        concentration = pd.DataFrame(
            columns=['parallel_id'],
        ).set_index('parallel_id', drop=True)
        statistics = pd.DataFrame(
            columns=['kind'],
        ).set_index('kind', drop=True)
        for sheet in find_sheets(xml.find('columns'), sheet_name=filtrated_by_sheet):
            for column in find_columns(sheet, label=filtrated_by_label):
                line = parse_column(column)

                for probe in column.findall('cells/pc'):
                    for parallel in probe.findall('cl'):
                        parallel_id = int(parallel.attrib['i'])

                        concentration.loc[parallel_id, line['nickname']] = parallel.attrib.get('v', '')

                    statistics.loc['Cред.', line['nickname']] = _parse_mean(probe)
                    statistics.loc['СКО', line['nickname']] = _parse_standard_deviation(probe)

        return AtomData(
            meta=meta,
            concentration=concentration,
            statistics=statistics,
        )


def _parse_mean(__probe: XML) -> str:

    element = __probe.find('am')
    if element is None:
        return ''

    return element.attrib.get('v', '')


def _parse_standard_deviation(probe: XML) -> str:

    element = probe.find('sr')
    if element is None:
        return ''

    return element.attrib.get('v', '')
