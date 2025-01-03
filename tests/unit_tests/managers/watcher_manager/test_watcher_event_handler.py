import shutil
from pathlib import Path
from uuid import uuid4

import pytest
from pytestqt.qtbot import QtBot

from aims.managers.watcher_manager import WatcherManager


class FileManager:

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def create_file(
        self,
        filename: str | None = None,
        text: str | None = None,
    ) -> None:
        filename = filename or f'{uuid4()}.xml'
        text = text or r'<?xml version="1.0"?>'

        filepath = self.directory / filename
        filepath.write_text(text)


@pytest.fixture
def file_manager(
    tmp_path: Path,
) -> FileManager:
    return FileManager(
        directory=tmp_path,
    )


def test_watcher_event_handler_create_xml(
    watcher_manager: WatcherManager,
    file_manager: FileManager,
    qtbot: QtBot,
):

    with qtbot.wait_signal(watcher_manager.event_handler.bridge.updated, timeout=10) as blocker:
        watcher_manager.setup(
            path=file_manager.directory,
        )

        file_manager.create_file()

    assert blocker.signal_triggered


def test_watcher_event_handler_modify_xml(
    watcher_manager: WatcherManager,
    file_manager: FileManager,
    qtbot: QtBot,
):
    filename = f'{uuid4()}.xml'
    file_manager.create_file(filename)

    with qtbot.wait_signal(watcher_manager.event_handler.bridge.updated, timeout=10) as blocker:
        watcher_manager.setup(
            path=file_manager.directory,
        )

        filepath = file_manager.directory / filename
        with open(filepath, 'a') as file:
            file.write(r'<analysis>\n</analysis>')

    assert blocker.signal_triggered


def test_watcher_event_handler_create_not_xml(
    watcher_manager: WatcherManager,
    file_manager: FileManager,
    qtbot: QtBot,
):

    with qtbot.assert_not_emitted(watcher_manager.event_handler.bridge.updated, wait=100):
        watcher_manager.setup(
            path=file_manager.directory,
        )

        file_manager.create_file(
            filename='text.txt',
            text='Hello, World!',
        )


def test_watcher_event_handler_create_directory(
    watcher_manager: WatcherManager,
    file_manager: FileManager,
    qtbot: QtBot,
):

    with qtbot.assert_not_emitted(watcher_manager.event_handler.bridge.updated, wait=100):
        watcher_manager.setup(
            path=file_manager.directory,
        )

        directory = file_manager.directory / 'tmp'
        directory.mkdir(parents=True, exist_ok=True)


def test_watcher_event_handler_delete_xml(
    watcher_manager: WatcherManager,
    file_manager: FileManager,
    qtbot: QtBot,
):
    filename = f'{uuid4()}.xml'
    file_manager.create_file(filename)

    with qtbot.assert_not_emitted(watcher_manager.event_handler.bridge.updated, wait=100):
        watcher_manager.setup(
            path=file_manager.directory,
        )

        filepath = file_manager.directory / filename
        filepath.unlink()


def test_watcher_event_handler_rename_xml(
    watcher_manager: WatcherManager,
    file_manager: FileManager,
    qtbot: QtBot,
):
    filename = f'{uuid4()}.xml'
    file_manager.create_file(filename)

    with qtbot.assert_not_emitted(watcher_manager.event_handler.bridge.updated, wait=100):
        watcher_manager.setup(
            path=file_manager.directory,
        )

        filepath = file_manager.directory / filename
        filepath.rename(file_manager.directory / f'{uuid4()}.xml')


@pytest.mark.skip(reason='How to move file correctly?')
def test_watcher_event_handler_move_xml(
    watcher_manager: WatcherManager,
    file_manager: FileManager,
    qtbot: QtBot,
):
    filename = f'{uuid4()}.xml'
    file_manager.create_file(filename)

    with qtbot.assert_not_emitted(watcher_manager.event_handler.bridge.updated, wait=100):
        watcher_manager.setup(
            path=file_manager.directory,
        )

        src = file_manager.directory / filename
        dst = file_manager.directory / str(uuid4()) / filename
        dst.mkdir(parents=True, exist_ok=True)
        shutil.move(src, dst)
