import os
import uuid
from pathlib import Path

import pytest

from aims.config import Directory
from aims.managers.data_manager.scrapers.scraper import walk


@pytest.fixture(params=[0, 1, 42])
def n_files(request) -> int:
    return request.param


@pytest.fixture
def expected(
    n_files: int,
    tmp_path: Path,
) -> tuple[str]:

    filepathes = []
    for _ in range(n_files):

        filepath = os.path.join(tmp_path, f'{uuid.uuid4()}.xml')
        with open(filepath, 'w') as file:
            file.write('')

        filepathes.append(filepath)

    return tuple(filepathes)


def test_walk(
    expected: tuple[str],
    tmp_path: Path,
):

    filepaths = tuple(walk(
        directory=Directory(str(tmp_path)),
    ))

    assert set(filepaths) == set(expected)
