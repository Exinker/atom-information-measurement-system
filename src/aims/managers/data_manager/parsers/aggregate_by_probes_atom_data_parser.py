import logging
from warnings import simplefilter

import pandas as pd

from aims.configs import Config, FiltratedLabel, FiltratedSheet
from aims.managers.data_manager.atom_data import AtomData
from aims.managers.data_manager.parsers.base_atom_data_parser import AtomDataParserABC
from aims.managers.data_manager.parsers.utils import (
    find_columns,
    find_sheets,
    parse_column,
)
from aims.managers.data_manager.types import XML, XMLPath
from aims.managers.data_manager.utils.formatters import normalize_datetime


simplefilter(action="ignore", category=pd.errors.PerformanceWarning)  # FIXME


LOGGER = logging.getLogger('app')


class AggregateByProbesAtomDataParser(AtomDataParserABC):

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
    ]

    def __init__(self, config: Config):
        super().__init__(config=config)

    def parse(
        self,
        __filepath: XMLPath,
        xml: XML,
    ) -> AtomData:
        """Get recorded data from Atom's .xml file."""

        LOGGER.debug('Parse XML: %r', __filepath)
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
            LOGGER.debug(
                'Probes: %s were parsed from %r',
                ', '.join(map(repr, data.meta['probe_name'].to_list())),
                __filepath,
            )
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
        ).set_index('probe_guid', drop=False)
        for __probe in xml.find('probes').findall('probe'):

            is_not_empty = len(__probe.findall('spe')) > 0
            if is_not_empty:
                probe_guid = parse_probe_guid(__probe)

                meta.loc[probe_guid, 'filepath'] = filepath
                meta.loc[probe_guid, 'organization_name'] = organization_name
                meta.loc[probe_guid, 'device_name'] = device_name
                meta.loc[probe_guid, 'user_name'] = user_name
                meta.loc[probe_guid, 'analysis_name'] = analysis_name
                meta.loc[probe_guid, 'probe_guid'] = probe_guid
                meta.loc[probe_guid, 'probe_id'] = int(__probe.attrib['id'])
                meta.loc[probe_guid, 'probe_name'] = __probe.attrib.get('name', '???')
                meta.loc[probe_guid, 'datetime'] = normalize_datetime(__probe.find('date[@type="last"]').text)
                meta.loc[probe_guid, 'is_certified'] = {
                    'yes': True,
                    'no': False,
                }.get(__probe.attrib.get('COC', 'no'))

        concentration = pd.DataFrame(
            columns=['probe_guid'],
        ).set_index('probe_guid', drop=True)
        for __sheet in find_sheets(xml.find('columns'), sheet_name=filtrated_by_sheet):
            for __column in find_columns(__sheet, label=filtrated_by_label):
                line = parse_column(__column)

                for __probe in __column.findall('cells/pc'):
                    probe_id = int(__probe.attrib['i'])
                    probe_guid = meta[meta['probe_id'] == probe_id]['probe_guid'].item()

                    concentration.loc[probe_guid, line['nickname']] = __probe.attrib.get('v', '')

        return AtomData(
            meta=meta,
            concentration=concentration,
        )


def parse_probe_guid(__probe: XML) -> str:
    # FIXME: remove capability with old version XML files!

    try:
        probe_guid = __probe.find('sample/guid').text
    except AttributeError:
        probe_guid = __probe.attrib['id']

    return probe_guid
