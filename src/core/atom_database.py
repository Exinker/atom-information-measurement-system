from dataclasses import dataclass

import pandas as pd

from .typing import AnalysisName, Frame, XML


@dataclass
class Tolerance:
    n_parallels: int
    dabs: float
    Dabs: float


@dataclass
class MeasurementToleranceDatabase:

    data: Frame | None

    def get_tolerance(self, symbol: str, conc: float) -> Tolerance | None:
        if self.data is None:
            return None

        #
        datum = self.data[self.data['symbol'] == symbol]
        datum = datum[(datum['conc_min'] < conc) & (conc <= datum['conc_max'])]

        #
        if datum.empty:
            return None

        return Tolerance(
            n_parallels=datum['n_parallels'].item(),
            dabs=datum['dabs'].item(),
            Dabs=datum['Dabs'].item(),
        )

    # --------        handlers        --------
    @classmethod
    def from_xml(cls, xml: XML, analysis_name: AnalysisName) -> 'MeasurementToleranceDatabase':
        """Get measurement tolerance database from Atom's .xml file."""
        analysis_name = {
            'Al 2023': 'ГОСТ 7727-81 Al сплавы',  # ('ГОСТ 3221-85 Al первичный', 'ГОСТ 7727-81 Al сплавы', )
        }.get(analysis_name, analysis_name)  # FIXME: remove it!

        for standart in xml.findall('norm'):
            if standart.attrib['title'] == analysis_name:

                data = pd.DataFrame(
                    columns=['symbol', 'c_min', 'c_max', 'n_parallels', 'dabs', 'Dabs'],
                )

                data = []
                for row in standart.findall('row'):
                    datum = {
                        'symbol': row.attrib['element'],
                        'conc_min': float(row.attrib['cmin']),
                        'conc_max': float(row.attrib['cmax']),
                        'n_parallels': int(row.find('npar').text),
                        'dabs': float(row.find('dabs').text),
                        'Dabs': float(row.find('Dabs').text),
                    }

                    data.append(datum)

                data = pd.DataFrame(
                    data,
                    columns=['symbol', 'conc_min', 'conc_max', 'n_parallels', 'dabs', 'Dabs'],
                )

                return MeasurementToleranceDatabase(data=data)

        return MeasurementToleranceDatabase(data=None)
