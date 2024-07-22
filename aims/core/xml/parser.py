import functools
import os
from datetime import datetime

import numpy as np
import pandas as pd

from aims.config import Config
from aims.core.formatters import normalize_name
from aims.core.scraper import load_xml
from aims.core.types import AnalysisName, Frame, ProbeName, XMLPath

from .data import AtomData


class Cache:
    instance = None
    storage = {}

    def __new__(cls) -> 'Cache':
        if cls.instance is None:
            cls.instance = super().__new__(cls)

        return cls.instance

    @classmethod
    def clear(cls) -> None:
        cls.storage = {}

    def __call__(self, __filepath: XMLPath, *args, analysis_name: AnalysisName, probe_name: ProbeName, **kwargs):
        key = hash((__filepath, analysis_name, probe_name))

        if key not in self.cache:
            self.cache[key] = self.func(self, __filepath, *args, analysis_name=analysis_name, probe_name=probe_name, **kwargs)

            if bool(os.environ['DEBUG']):
                print(f'parsed: {__filepath}')

        return self.cache[key]


def cache(func):
    cache = Cache()

    @functools.wraps(func)
    def wrapped(self, __filepath: XMLPath, *args, analysis_name: AnalysisName, probe_name: ProbeName, **kwargs):
        key = hash((__filepath, analysis_name, probe_name))

        if key not in cache.storage:
            cache.storage[key] = func(self, __filepath, *args, analysis_name=analysis_name, probe_name=probe_name, **kwargs)

            if bool(os.environ['DEBUG']):
                print(f'parsed: {__filepath}')

        return cache.storage[key]

    return wrapped


class Parser:

    def __init__(self, config: Config):
        self.config = config

    @cache
    def parse(self, __filepath: XMLPath, analysis_name: AnalysisName, probe_name: ProbeName) -> tuple[Frame, Frame, Frame]:
        """Парсить .xml файл для ."""

        # atom data
        xml = load_xml(__filepath)

        atom_data = AtomData.from_xml(
            xml=xml,
            filtrated_by_sheet=self.config.filtrated_by_sheet,
            filtrated_by_label=self.config.filtrated_by_label,
        )

        # TODO: remove it!
        # filtrate probes
        # n_probes, _ = atom_data.probes.shape

        # cond = np.full(n_probes, True)
        # for j in range(n_probes):

        #     # check: probe's name
        #     cond[j] = cond[j] and normalize_name(
        #         name=atom_data.probes.iloc[j]['name'],
        #         sep=history.sep,
        #     ) == probe_name

        #     # check: probe's created datetime
        #     cond[j] = cond[j] and config.tracked_period.check(
        #         atom_data.probes.iloc[j]['datetime'],
        #         milestone=history.milestone,
        #     )

        # parse probes
        filedir, filename = os.path.split(__filepath)

        meta = []
        reference = []
        prediction = []
        for probe_id in atom_data.probes.index:

            meta.append({
                'file_dir': filedir,
                'file_name': filename,
                'datetime': atom_data.probes.loc[probe_id, 'datetime'],
                'analysis_name': atom_data.meta.analysis_name,
                'organization_name': atom_data.meta.organization_name,
                'device_name': atom_data.meta.device_name,
                'user_name': atom_data.meta.user_name,
                'probe_name': atom_data.probes.loc[probe_id, 'name'],
                'is_certified': atom_data.probes.loc[probe_id, 'is_certified'],
            })

            reference.append(dict(
                **{
                    symbol: value
                    for symbol, value in atom_data.reference.loc[probe_id].to_dict().items()
                },
            ))

            prediction.append(dict(
                **{
                    atom_data.lines.loc[line_id, 'symbol'] + ' ' + str(atom_data.lines.loc[line_id, 'wavelength']): values
                    for line_id, values in atom_data.prediction.loc[probe_id].to_dict().items()
                },
            ))

        #
        return pd.DataFrame(meta), pd.DataFrame(reference), pd.DataFrame(prediction)
