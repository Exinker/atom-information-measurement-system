from typing import Generator

import pytest

from aims.managers.data_manager import DataManager
from aims.managers.watcher_manager import WatcherManager
from tests.fakes.managers import FakeCallback


@pytest.fixture
def fake_callback():
    return FakeCallback()


@pytest.fixture
def data_manager():
    return DataManager()


@pytest.fixture
def watcher_manager(
    data_manager: DataManager,
    fake_callback: FakeCallback,
) -> Generator[WatcherManager, None, None]:
    watcher_manager = WatcherManager(
        data_manager=data_manager,
        callback=fake_callback,
    )
    yield watcher_manager

    watcher_manager.observer.stop()
