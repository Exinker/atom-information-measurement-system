import os
import subprocess

from aims.config import EXPLORER

from .types import XMLPath


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
