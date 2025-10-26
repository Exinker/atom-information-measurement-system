import os
from typing import Iterator

from aims.configs import Directory
from spectrumapp.types import FilePath


def walk(
    directory: Directory,
) -> Iterator[FilePath]:
    """Walk iterable along for a given path."""

    for filedir, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(filedir, filename)

            yield filepath
