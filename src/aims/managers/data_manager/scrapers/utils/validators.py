import os
from datetime import datetime

from aims.config import TrackedPediod
from aims.managers.data_manager.types import XML, XMLPath


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
    xml: XML,
) -> bool:
    """Validate `xml` to simplest cases."""

    if xml.tag != 'analysis':
        return False

    if any(xml.find(tag) is None for tag in (
        # 'guid',
        'file',
        'titul',
        'probes',
        'columns',
    )):
        return False

    return True
