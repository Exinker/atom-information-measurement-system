from datetime import datetime

from aims.managers.data_manager.types import ProbeName


def normalize_name(
    name: ProbeName,
    sep: str,
) -> ProbeName:
    """Normalize `name`."""

    # remove a comment after the last `sep`.
    if sep and (sep in name):
        name, _ = name.rsplit(sep, maxsplit=1)

    # lowercase and remove spaces at the right
    name = name.lower()
    name = name.rstrip()

    return name


def normalize_datetime(
    created_at: str,
) -> datetime:
    """Normalize `created_at` datetime."""

    return datetime.fromisoformat(created_at)
