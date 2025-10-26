import os
from pathlib import Path
from typing import Callable

import pytest
from pytest import MonkeyPatch

from aims.configs import (
    Config,
    Directory,
    FiltratedLabel,
    TrackedMode,
    TrackedPediod,
    setdefault_config,
)


@pytest.fixture
def assert_default_config() -> Callable[[Config], None]:

    def inner(
        config: Config,
    ) -> None:
        assert config.version == os.environ['APPLICATION_VERSION']
        assert config.directory == Directory.default()
        assert config.tracked_mode == TrackedMode.default()
        assert config.tracked_period == TrackedPediod.default()
        assert config.tracked_analisys_name == ''
        assert config.tracked_probe_name == ''
        assert config.tracked_queue_length == 5
        assert config.filtrated_by_sheet is None
        assert config.filtrated_by_label == FiltratedLabel.default()
        assert config.sep == '*'

    return inner


def test_config_default(
    assert_default_config: Callable[[Config], None],
):
    config = Config.default()

    assert_default_config(config)


@pytest.fixture
def filepath(
    tmp_path: Path,
) -> str:

    filepath = str(tmp_path / 'config.json')
    assert not os.path.exists(filepath)

    return filepath


@pytest.fixture
def expected(
    filepath: str,
    monkeypatch: MonkeyPatch,
) -> Config:
    monkeypatch.setattr(Config, 'FILEPATH', filepath)

    config = Config.default()
    config.dump()

    return config


def test_config_load(
    expected: Config,
):
    config = Config.load()

    assert config == expected


def test_setdefault_config(
    filepath: str,
    monkeypatch: MonkeyPatch,
) -> Config:
    monkeypatch.setattr(Config, 'FILEPATH', filepath)

    setdefault_config()

    assert os.path.exists(filepath)


@pytest.mark.parametrize(
    'force', [True, False],
)
def test_setdefault_config_forced(
    filepath: str,
    force: bool,
    monkeypatch: MonkeyPatch,
    mocker,
) -> Config:
    spy = mocker.spy(Config, 'default')
    monkeypatch.setattr(Config, 'FILEPATH', filepath)
    config = Config.default()
    config.dump()

    setdefault_config(force=force)

    assert os.path.exists(filepath)
    assert spy.call_count == 1 + force
