import logging
import os
import subprocess

from aims.config import EXPLORER
from aims.core.types import XMLPath


LOGGER = logging.getLogger('app')


def run_explorer(path: XMLPath):
    """Run explorer with selected path."""

    if not EXPLORER:
        return

    try:
        LOGGER.info(
            'Open explorer in: %r',
            path,
        )

        path = os.path.normpath(path)
        if os.path.isdir(path):
            subprocess.run([EXPLORER, f'{path}'])
        if os.path.isfile(path):
            subprocess.run([EXPLORER, '/select,', f'{path}'])

    except (TypeError, FileNotFoundError):  # TODO: refactor
        pass
