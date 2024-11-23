from warnings import simplefilter

import pandas as pd

from aims.config import Config, FiltratedLabel, FiltratedSheet
from aims.core.atom_data import AtomData
from aims.core.parsers.parsers.atom_data_parsers.base_atom_data_parser import AtomDataParserABC
from aims.core.parsers.parsers.atom_meta_parsers import MetaParser
from aims.core.parsers.parsers.utils import (
    find_columns,
    find_sheets,
    parse_column,
)
from aims.core.types import XML
from aims.core.utils.formatters import normalize_datetime


simplefilter(action="ignore", category=pd.errors.PerformanceWarning)  # FIXME


class AggregateByParallelsAtomDataParser(AtomDataParserABC):

    def __init__(self, config: Config):
        super().__init__(config=config)

    def parse(self, xml: XML) -> AtomData:
        """Get recorded data from Atom's .xml file."""

        return self._parse(
            xml=xml,
            filtrated_by_sheet=self.config.filtrated_by_sheet,
            filtrated_by_label=self.config.filtrated_by_label,
        )

    @staticmethod
    def _parse(xml: XML, filtrated_by_sheet: FiltratedSheet, filtrated_by_label: FiltratedLabel) -> AtomData:
        """Get recorded data from Atom's .xml file."""

        meta = MetaParser().parse(xml=xml)

        parallels = pd.DataFrame(
            columns=['guid', 'id', 'name', 'datetime', 'is_certified'],
        ).set_index('guid', drop=False)
        for probe in xml.find('probes').findall('probe'):

            is_not_empty = len(probe.findall('spe')) > 0
            if is_not_empty:
                is_certified = {
                    'yes': True,
                    'no': False,
                }.get(probe.attrib.get('COC', 'no'))

                for parallel in probe.findall('spe'):
                    parallel_id = int(parallel.attrib['id'])

                    parallels.loc[parallel_id, 'id'] = parallel_id
                    parallels.loc[parallel_id, 'name'] = parallel.attrib.get('name', '???')
                    parallels.loc[parallel_id, 'datetime'] = normalize_datetime(parallel.find('date').text)
                    parallels.loc[parallel_id, 'is_certified'] = is_certified

        concentration = pd.DataFrame(
            columns=['parallel_id'],
        ).set_index('parallel_id', drop=True)
        statistics = pd.DataFrame(
            columns=['parallel_id'],
        ).set_index('parallel_id', drop=True)
        for sheet in find_sheets(xml.find('columns'), sheet_name=filtrated_by_sheet):
            for column in find_columns(sheet, label=filtrated_by_label):
                line = parse_column(column)

                for probe in column.findall('cells/pc'):
                    for parallel in probe.findall('cl'):
                        parallel_id = int(parallel.attrib['i'])

                        concentration.loc[parallel_id, line['line_id']] = parallel.attrib.get('v', '')

                    statistics.loc['Cред.', line['line_id']] = probe.find('am').attrib.get('v', '')
                    statistics.loc['СКО', line['line_id']] = probe.find('sr').attrib.get('v', '')

        return AtomData(
            meta=meta,
            rows=parallels,
            reference=concentration,
            concentration=concentration,
            statistics=statistics,
        )
