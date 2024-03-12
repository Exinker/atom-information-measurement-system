from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from .config import FiltratedLabel, FiltratedSheet
from .typing import AnalysisName, Frame, XML
from .utils import normalize_datetime


# --------        Meta        --------
@dataclass
class Meta:
    organization_name: str
    device_name: str
    user_name: str
    analysis_name: AnalysisName

    @classmethod
    def from_xml(cls, xml: XML) -> 'Meta':
        """Get recorded meta from Atom's .xml file."""

        # parse
        organization_name = xml.find('titul').find('organization').text
        device_name = xml.find('titul').find('device').text
        user_name = xml.find('titul').find('user').text
        analysis_name = xml.find('titul').find('aname').text

        return cls(
            organization_name=organization_name,
            device_name=device_name,
            user_name=user_name,
            analysis_name=analysis_name,
        )


# --------        AtomData        --------
def _find_sheets(element: XML, sheet_name: FiltratedSheet) -> list[XML]:
    """Find sheets for a given name (or return all sheets)."""

    if sheet_name is None:
        return element.findall('sheet')

    sheets = element.findall(f'sheet[@name="{sheet_name}"]')
    if sheets:
        return sheets
    return element.findall('sheet')


def _find_line_columns(element: XML, label: FiltratedLabel) -> list[XML]:
    """Find columns for a given label."""

    if label in (FiltratedLabel.NONE, ):
        return element.findall('column[@type="line"]')

    if label in (FiltratedLabel.ENGINEAR, FiltratedLabel.LABORANT, FiltratedLabel.REPORT):
        key = {
            'enginear': 'visible',
        }.get(label.value, label.value)

        return element.findall(f'column[@type="line"][@{key}="yes"]')

    raise AssertionError(f'Filtrated label {label.value} is not used!.')


@dataclass
class AtomData:
    meta: Meta
    probes: Frame
    lines: Frame
    prediction: Frame
    reference: Frame

    @classmethod
    def from_xml(cls, xml: XML, filtrated_by_sheet: FiltratedSheet, filtrated_by_label: FiltratedLabel) -> 'AtomData':
        """Get recorded data from Atom's .xml file."""

        # parse meta
        meta = Meta.from_xml(xml=xml)

        # parse probes
        probes = pd.DataFrame(
            columns=['id', 'name', 'datetime_created', 'datetime_updated', 'is_ref'],
        ).set_index('id', drop=False)

        for probe in xml.find('probes').findall('probe'):

            n_parallels = len(probe.findall('spe'))
            if n_parallels > 0:
                probe_id = int(probe.attrib['id'])
                datetimes = [normalize_datetime(parallel.find('date').text) for parallel in probe.findall('spe')]

                probes.loc[probe_id, 'id'] = probe_id
                probes.loc[probe_id, 'name'] = probe.attrib.get('name', '???')
                probes.loc[probe_id, 'datetime_created'] = min(datetimes)
                probes.loc[probe_id, 'datetime_updated'] = max(datetimes)
                probes.loc[probe_id, 'is_certified'] = {
                    'yes': True,
                    'no': False,
                }.get(probe.attrib.get('COC', 'no'))

        # parse lines, prediction, reference
        lines = pd.DataFrame(
            columns=['id', 'symbol', 'wavelength'],
        ).set_index('id', drop=False)

        prediction = pd.DataFrame(
            columns=['probe_id'],
        ).set_index('probe_id', drop=True)

        reference = pd.DataFrame(
            columns=['probe_id', 'symbol'],
        ).set_index('probe_id', drop=False)

        for sheet in _find_sheets(xml.find('columns'), sheet_name=filtrated_by_sheet):
            for column in _find_line_columns(element=sheet, label=filtrated_by_label):

                line_id = int(column.attrib['id'])
                symbol = column.find('element').text

                lines.loc[line_id, 'id'] = line_id
                lines.loc[line_id, 'symbol'] = symbol
                lines.loc[line_id, 'wavelength'] = column.find('wl').text

                for probe in column.findall('cells/pc'):
                    probe_id = int(probe.attrib['i'])

                    prediction.loc[probe_id, line_id] = probe.attrib.get('v', '')
                    reference.loc[probe_id, symbol] = probe.attrib.get('cm', '')

        #
        return cls(
            meta=meta,
            probes=probes,
            lines=lines,
            reference=reference,
            prediction=prediction,
        )
