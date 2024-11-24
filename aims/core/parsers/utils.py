from typing import Iterable

import pandas as pd

from aims.config import FiltratedLabel, FiltratedSheet
from aims.core.types import Series, XML


def find_sheets(__xml: XML, sheet_name: FiltratedSheet) -> Iterable[XML]:
    """Find sheets for a given name (or return all sheets)."""

    if sheet_name is None:
        return __xml.findall('sheet')

    sheets = __xml.findall(f'sheet[@name="{sheet_name}"]')
    if sheets:
        return sheets
    return __xml.findall('sheet')


def find_columns(__xml: XML, label: FiltratedLabel) -> Iterable[XML]:
    """Find columns for a given label."""

    def _filtrate_by_type(__column: XML) -> bool:
        """Filtrate column by type."""

        return __column.attrib['type'] in ['line', 'commonLine']

    def _filtrate_by_label(__column: XML, label: FiltratedLabel) -> bool:
        """Filtrate column by label."""

        if label in [FiltratedLabel.NONE]:
            return True

        if label in [FiltratedLabel.LABORANT, FiltratedLabel.ENGINEAR, FiltratedLabel.REPORT]:
            key = {
                'enginear': 'visible',
            }.get(label.value, label.value)
            return __column.attrib[key] == 'yes'

        raise AssertionError(f'Filtrated label {label.value} is not used!.')

    for column in __xml.findall('column'):
        if _filtrate_by_type(column) and _filtrate_by_label(column, label=label):
            yield column


def parse_column(__column: XML) -> Series:
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
