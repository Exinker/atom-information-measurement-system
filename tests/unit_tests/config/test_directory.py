import os
import uuid
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from aims.config import Directory


def test_directory():
    directory = Directory(
        path=os.getcwd(),
    )

    assert directory == os.getcwd()


def test_directory_not_exists():

    with pytest.raises(ValueError):
        Directory(
            path=os.path.join(os.getcwd(), str(uuid.uuid4())),
        )


def test_directory_default():
    directory = Directory.default()

    assert directory == os.getcwd()


@pytest.fixture
def path(
    tmp_path: Path,
) -> str:
    path = tmp_path / 'AIMS'
    path.mkdir(parents=True, exist_ok=True)

    return str(path)


@pytest.fixture
def expected(
    tmp_path: Path,
) -> str:
    path = tmp_path / 'DB'
    path.mkdir(parents=True, exist_ok=True)

    return str(path)


def test_directory_default_in_atom_folder(
    path: str,
    expected: str,
    monkeypatch: MonkeyPatch,
):
    monkeypatch.setattr('os.getcwd', lambda: path)

    directory = Directory.default()

    assert directory == expected
