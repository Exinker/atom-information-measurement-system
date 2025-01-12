import os
from datetime import datetime
from typing import Iterator

from aims.config import Directory, TrackedPediod
from aims.managers.data_manager.types import XML, XMLPath
from spectrumapp.types import FilePath


def walk(
    directory: Directory,
) -> Iterator[FilePath]:
    """Walk iterable along for a given path."""

    for filedir, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(filedir, filename)

            yield filepath


def validate_file(
    filepath: XMLPath,
    milestone: datetime,
    tracked_period: TrackedPediod,
) -> bool:
    """Validate file to the simplest cases."""

    if not filepath.endswith('.xml'):
        return False

    created_at = datetime.fromtimestamp(
        timestamp=os.stat(filepath).st_ctime,
    )
    if not tracked_period.check(created_at, milestone=milestone):
        return False

    return True


def validate_xml(
    xml: XML | None,
) -> bool:
    """Validate `xml` to simplest cases."""

    if xml is None:
        return False

    if xml.tag != 'analysis':
        return False

    if xml.find('titul') is None:
        return False

    titul = xml.find('titul')
    if any(
        titul.find(tag) is None
        for tag in ('organization', 'device', 'user', 'date', 'aname')
    ):
        return False

    probes = xml.find('probes')
    if probes is None:
        return False

    columns = xml.find('columns')
    if columns is None:
        return False

    return True
