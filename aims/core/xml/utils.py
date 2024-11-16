import os
import xml.etree.ElementTree as ElementTree
from datetime import datetime
from typing import Iterator

from aims.config import Directory, TrackedPediod
from aims.core.types import XML, XMLPath


def walk(directory: Directory) -> Iterator[XMLPath]:
    """Walk iterable along for a given path."""

    for filedir, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(filedir, filename)

            yield filepath


def validate_file(filepath: XMLPath, milestone: datetime, tracked_period: TrackedPediod) -> bool:
    """Validate file to the simplest cases."""

    # validate file's extension
    if not filepath.endswith('.xml'):
        return False

    # validate file's created datetime
    filestat = os.stat(filepath)

    created_at = datetime.fromtimestamp(filestat.st_ctime)
    if not tracked_period.check(created_at, milestone=milestone):
        return False

    #
    return True


def load_xml(filepath: XMLPath) -> XML | None:
    """Load `xml` element object from file for a given `filepath`."""

    try:
        tree = ElementTree.parse(filepath)
        xml = tree.getroot()

        return xml

    except Exception:
        return None


def validate_xml(xml: XML | None) -> bool:
    """Validate `xml` to simplest cases."""

    if xml is None:
        return False

    # check analysis
    if xml.tag != 'analysis':
        return False

    # check titul
    titul = xml.find('titul')
    if titul is None:
        return False

    if any(titul.find(tag) is None for tag in ['organization', 'device', 'user', 'date', 'aname']):
        return False

    # check probes
    probes = xml.find('probes')
    if probes is None:
        return False

    # check columns
    columns = xml.find('columns')
    if columns is None:
        return False

    #
    return True
