
import os
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime

from .alias import ProbeName, XML, XMLPath
from .config import EXPLORER


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


def load_xml(path: XMLPath) -> XML | None:
    """Load `xml` element object from file for a given `path`."""
    # TODO: check Atom's xml

    try:
        tree = ET.parse(path)
        xml = tree.getroot()

        return xml

    except Exception:  # TODO: refactor
        return None


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
