import logging
import os
import pandas as pd

from aims.core.types import Frame
from aims.core.xml.utils import load_xml
from aims.core.xml.parsers.cache import cache

from .aggregate_by_probes_data_parser import AggregateByProbeDataParser
from .base_data_parser import DataParserABC


LOGGER = logging.getLogger('app')


@cache
def parse_data(
    __filepath: str,
    data_parser: DataParserABC,
) -> tuple[Frame, Frame, Frame]:
    xml = load_xml(__filepath)

    data = data_parser.parse(xml=xml)
    filedir, filename = os.path.split(__filepath)

    meta = []
    reference = []
    prediction = []
    for probe_id in data.probes.index:
        meta.append({
            'file_dir': filedir,
            'file_name': filename,
            'datetime': data.probes.loc[probe_id, 'datetime'],
            'analysis_name': data.meta.analysis_name,
            'organization_name': data.meta.organization_name,
            'device_name': data.meta.device_name,
            'user_name': data.meta.user_name,
            'probe_name': data.probes.loc[probe_id, 'name'],
            'is_certified': data.probes.loc[probe_id, 'is_certified'],
        })
        prediction.append(dict(
            **{
                data.lines.loc[line_id, 'nickname']: values
                for line_id, values in data.prediction.loc[probe_id].to_dict().items()
            },
        ))
        reference.append(dict(
            **{
                symbol: value
                for symbol, value in data.reference.loc[probe_id].to_dict().items()
            },
        ))

    return pd.DataFrame(meta), pd.DataFrame(reference), pd.DataFrame(prediction)


__all__ = [
    AggregateByProbeDataParser,
    DataParserABC,
    parse_data,
]
