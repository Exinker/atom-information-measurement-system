import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd
import pytest

from aims.configs import TrackedPediod
from aims.managers.data_manager.scrapers.utils.validators import validate_file
from spectrumapp.types import FilePath


@pytest.fixture
def filepath(
    tmp_path: Path,
) -> Callable[[str], FilePath]:

    def wrapper(suffix: str) -> FilePath:
        filepath = os.path.join(tmp_path, f'{uuid.uuid4()}.{suffix}')
        with open(filepath, 'w') as file:
            file.write('')

        return filepath
    return wrapper


@pytest.fixture
def milestone() -> datetime:
    return datetime.now()


def test_validate_file(
    filepath: Callable[[str], FilePath],
    milestone: datetime,
):

    status = validate_file(
        filepath=filepath('xml'),
        milestone=milestone,
        tracked_period=TrackedPediod.default(),
    )

    assert status is True


@pytest.mark.parametrize(
    'suffix', ['txt', 'json'],
)
def test_validate_file_wrong_suffix(
    suffix: str,
    filepath: Callable[[str], FilePath],
    milestone: datetime,
):

    status = validate_file(
        filepath=filepath(suffix),
        milestone=milestone,
        tracked_period=TrackedPediod.default(),
    )

    assert status is False


def test_validate_file_wrong_timestamp(
    filepath: Callable[[str], FilePath],
    milestone: datetime,
):

    status = validate_file(
        filepath=filepath('xml'),
        milestone=milestone + pd.offsets.DateOffset(weeks=1),
        tracked_period=TrackedPediod.DAY,
    )

    assert status is False
