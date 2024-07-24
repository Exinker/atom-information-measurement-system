from dataclasses import dataclass
from typing import Iterable, Iterator, Mapping
from warnings import simplefilter

import pandas as pd

from aims.config import FiltratedLabel, FiltratedSheet
from aims.core.formatters import normalize_datetime
from aims.core.types import Frame, Series, XML

from .meta import AtomMeta


simplefilter(action="ignore", category=pd.errors.PerformanceWarning)  # FIXME


@dataclass
class AtomData:
    meta: AtomMeta
    probes: Frame
    lines: Frame
    prediction: Frame
    reference: Frame

    # --------        factory        --------
    @classmethod
    def from_xml(cls, xml: XML, filtrated_by_sheet: FiltratedSheet, filtrated_by_label: FiltratedLabel) -> 'AtomData':
        """Get recorded data from Atom's .xml file."""

        # parse meta
        meta = AtomMeta.from_xml(xml=xml)

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
        for sheet in _find_sheets(xml.find('columns'), sheet_name=filtrated_by_sheet):
            for column in _find_columns(sheet, label=filtrated_by_label):
                line = _parse_column(column)
                lines.append(line)

                for probe in column.findall('cells/pc'):
                    probe_id = int(probe.attrib['i'])

                    prediction.loc[probe_id, line['line_id']] = probe.attrib.get('v', '')
                    reference.loc[probe_id, line['symbol']] = probe.attrib.get('cm', '')

        #
        return cls(
            meta=meta,
            probes=probes,
            lines=pd.DataFrame(
                lines,
                columns=['line_id', 'symbol', 'wavelength', 'nickname'],
            ).set_index('line_id', drop=False),
            reference=reference,
            prediction=prediction,
        )


# --------        private        --------
def _find_sheets(__xml: XML, sheet_name: FiltratedSheet) -> Iterable[XML]:
    """Find sheets for a given name (or return all sheets)."""

    if sheet_name is None:
        return __xml.findall('sheet')

    sheets = __xml.findall(f'sheet[@name="{sheet_name}"]')
    if sheets:
        return sheets
    return __xml.findall('sheet')


def _find_columns(__xml: XML, label: FiltratedLabel) -> Iterable[XML]:
    """Find columns for a given label."""

    def _filtrate_by_type(__column: XML) -> bool:
        """Filtrate column by type."""

        return __column.attrib['type'] in ('line', 'commonLine')

    
    def _filtrate_by_label(__column: XML, label: FiltratedLabel) -> bool:
        """Filtrate column by label."""

        if label in (FiltratedLabel.NONE, ):
            return True

        if label in (FiltratedLabel.LABORANT, FiltratedLabel.ENGINEAR, FiltratedLabel.REPORT, ):
            key = {
                'enginear': 'visible',
            }.get(label.value, label.value)
            return __column.attrib[key] == 'yes'

        raise AssertionError(f'Filtrated label {label.value} is not used!.')

    for column in __xml.findall('column'):
        if _filtrate_by_type(column) and _filtrate_by_label(column, label=label):
            yield column


def _parse_column(__column: XML) -> Series:
    """Pares `column` to `line` series."""

    return pd.Series({
        'line_id': _parse_line_id(__column),
        'symbol': _parse_line_symbol(__column),
        'wavelength': _parse_line_wavelength(__column),
        'nickname': _parse_line_nickname(__column),
    })


def _parse_line_id(__column: XML) -> int:
    """Parse `id` of the line."""

    return int(__column.attrib['id'])


def _parse_line_symbol(__column: XML) -> str:
    """Parse `symbol` of the line."""

    try:
        return __column.find('element').text
    except Exception:
        print()


def _parse_line_wavelength(__column: XML) -> str:
    """Parse `wavelength` of the line."""

    value = __column.find('wl')
    if value is None:
        return ''

    return value.text


def _parse_line_nickname(__column: XML) -> str:
    """Parse `nickname` of the line."""

    return __column.attrib['name']

