import os
import subprocess
from datetime import datetime

from .config import EXPLORER
from .typing import ProbeName, XMLPath


def normalize_name(name: ProbeName, sep: str) -> ProbeName:
    """Normalize `name`."""

    # remove a comment after the last `sep`.
    if sep and (sep in name):
        name, comment = name.rsplit(sep, maxsplit=1)

    # lowercase and remove spaces at the right
    name = name.lower()
    name = name.rstrip()

    #
    return name


def normalize_datetime(dt: str) -> datetime:
    """Normalize `datetime`."""
    return datetime.fromisoformat(dt)


def run_explorer(path: XMLPath):
    """Run explorer with selected path."""

    if not EXPLORER:
        return

    try:
        path = os.path.normpath(path)

        if os.path.isdir(path):
            subprocess.run([EXPLORER, f'{path}'])

        if os.path.isfile(path):
            subprocess.run([EXPLORER, '/select,', f'{path}'])

    except (TypeError, FileNotFoundError):  # TODO: refactor
        pass
