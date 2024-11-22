import logging
from warnings import simplefilter

import pandas as pd

from aims.config import Config, FiltratedLabel, FiltratedSheet
from aims.core.data import AtomData
from aims.core.formatters import normalize_datetime
from aims.core.types import XML
from aims.core.xml.parsers.data_parsers.base_data_parser import DataParserABC
from aims.core.xml.parsers.meta_parsers import MetaParser
from aims.core.xml.parsers.utils import (
    find_columns,
    find_sheets,
    parse_column,
)


simplefilter(action="ignore", category=pd.errors.PerformanceWarning)  # FIXME


LOGGER = logging.getLogger('app')


class AggregateByProbesDataParser(DataParserABC):

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
    def _parse(xml: XML, filtrated_by_sheet: FiltratedSheet, filtrated_by_label: FiltratedLabel) -> AtomData:
        """Get recorded data from Atom's .xml file."""

        # parse meta
        meta = MetaParser().parse(xml=xml)

        # parse probes
        probes = pd.DataFrame(
            columns=['id', 'name', 'datetime', 'is_certified'],
        ).set_index('id', drop=False)

        for probe in xml.find('probes').findall('probe'):

            is_not_empty = len(probe.findall('spe')) > 0
            if is_not_empty:
                probe_id = int(probe.attrib['id'])

                probes.loc[probe_id, 'id'] = probe_id
                probes.loc[probe_id, 'name'] = probe.attrib.get('name', '???')
                probes.loc[probe_id, 'datetime'] = normalize_datetime(probe.find('date[@type="last"]').text)
                probes.loc[probe_id, 'is_certified'] = {
                    'yes': True,
                    'no': False,
                }.get(probe.attrib.get('COC', 'no'))

        # parse lines, prediction, reference
        lines = []

        prediction = pd.DataFrame(
            columns=['probe_id'],
        ).set_index('probe_id', drop=True)
        reference = pd.DataFrame(
            columns=['probe_id', 'symbol'],
        ).set_index('probe_id', drop=False)
        for sheet in find_sheets(xml.find('columns'), sheet_name=filtrated_by_sheet):
            for column in find_columns(sheet, label=filtrated_by_label):
                line = parse_column(column)
                lines.append(line)

                for probe in column.findall('cells/pc'):
                    probe_id = int(probe.attrib['i'])

                    prediction.loc[probe_id, line['line_id']] = probe.attrib.get('v', '')
                    reference.loc[probe_id, line['symbol']] = probe.attrib.get('cm', '')

        return AtomData(
            meta=meta,
            probes=probes,
            lines=pd.DataFrame(
                lines,
                columns=['line_id', 'symbol', 'wavelength', 'nickname'],
            ).set_index('line_id', drop=False),
            reference=reference,
            prediction=prediction,
        )
