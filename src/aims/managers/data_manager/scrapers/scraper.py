import logging
import os
from datetime import datetime
from typing import Iterator

import pandas as pd

from aims.configs import Directory, TrackedPediod
from aims.managers.data_manager.scrapers.utils import scrape_xml
from aims.managers.data_manager.types import Frame
from spectrumapp.types import FilePath


LOGGER = logging.getLogger('app')


class Scraper:

    def __init__(
        self,
        milestone: datetime,
        directory: Directory,
        tracked_period: TrackedPediod,
        sep: str,
        verbose: bool = False,
    ) -> None:
        self.milestone = milestone
        self.directory = directory
        self.tracked_period = tracked_period
        self.sep = sep

        self.verbose = verbose

    def scrape(self) -> Frame:

        records = []
        for filepath in walk(self.directory):

            _records = scrape_xml(
                filepath,
                milestone=self.milestone,
                tracked_period=self.tracked_period,
                sep=self.sep,
            )
            records.extend(_records)

            if LOGGER.isEnabledFor(level=logging.DEBUG):
                probe_names = pd.DataFrame(
                    _records,
                    columns=['analysis_name', 'probe_name', 'probe_guid', 'datetime', 'path'],
                )['probe_name'].unique().tolist()
                LOGGER.debug(
                    'Probes %s were scraped from %r',
                    ', '.join(map(repr, probe_names)),
                    filepath,
                )

        records = pd.DataFrame(
            records,
            columns=['analysis_name', 'probe_name', 'probe_guid', 'datetime', 'path'],
        )
        return records


def walk(
    directory: Directory,
) -> Iterator[FilePath]:
    """Walk iterable along for a given path."""

    for filedir, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(filedir, filename)

            yield filepath
