import logging
from warnings import simplefilter

import pandas as pd

from aims.config import Config, FiltratedLabel, FiltratedSheet
from aims.core.atom_data import AtomData
from aims.core.utils.formatters import normalize_datetime
from aims.core.types import XML
from aims.core.parsers.parsers.atom_data_parsers.base_atom_data_parser import AtomDataParserABC
from aims.core.parsers.parsers.atom_meta_parsers import MetaParser
from aims.core.parsers.parsers.utils import (
    find_columns,
    find_sheets,
    parse_column,
)


simplefilter(action="ignore", category=pd.errors.PerformanceWarning)  # FIXME


LOGGER = logging.getLogger('app')


class AggregateByProbesAtomDataParser(AtomDataParserABC):

    def __init__(self, config: Config):
        super().__init__(config=config)

    def parse(self, xml: XML) -> AtomData:
        """Get recorded data from Atom's .xml file."""

        LOGGER.debug('Parse XML.')
        try:
            data = self._parse(
                xml=xml,
                filtrated_by_sheet=self.config.filtrated_by_sheet,
                filtrated_by_label=self.config.filtrated_by_label,
            )
        except Exception as error:
            LOGGER.warning(
                'XML parse failed with error: %s',
                error,
            )
            raise
        else:
            LOGGER.debug('XML is parsed.')
            return data

    @staticmethod
    def _parse(
        xml: XML,
        filtrated_by_sheet: FiltratedSheet,
        filtrated_by_label: FiltratedLabel,
    ) -> AtomData:
        """Get recorded data from Atom's .xml file."""
        meta = MetaParser().parse(xml=xml)

        probes = pd.DataFrame(
            columns=['probe_guid', 'id', 'name', 'datetime', 'is_certified'],
        ).set_index('probe_guid', drop=False)
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
                probes.loc[probe_guid, 'name'] = probe.attrib.get('name', '???')
                probes.loc[probe_guid, 'datetime'] = normalize_datetime(probe.find('date[@type="last"]').text)
                probes.loc[probe_guid, 'is_certified'] = {
                    'yes': True,
                    'no': False,
                }.get(probe.attrib.get('COC', 'no'))

        concentration = pd.DataFrame(
            columns=['probe_guid'],
        ).set_index('probe_guid', drop=True)
        reference = pd.DataFrame(
            columns=['probe_guid', 'symbol'],
        ).set_index('probe_guid', drop=False)
        for sheet in find_sheets(xml.find('columns'), sheet_name=filtrated_by_sheet):
            for column in find_columns(sheet, label=filtrated_by_label):
                line = parse_column(column)

                for probe in column.findall('cells/pc'):
                    probe_id = int(probe.attrib['i'])
                    probe_guid = probes[probes['id'] == probe_id]['probe_guid'].item()

                    concentration.loc[probe_guid, line['nickname']] = probe.attrib.get('v', '')
                    reference.loc[probe_guid, line['symbol']] = probe.attrib.get('cm', '')

        return AtomData(
            meta=meta,
            rows=probes,
            reference=reference,
            concentration=concentration,
        )
