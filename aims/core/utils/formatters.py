from datetime import datetime

from aims.core.types import ProbeName


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
