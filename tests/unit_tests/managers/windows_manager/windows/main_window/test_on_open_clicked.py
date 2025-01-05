from functools import wraps
from pathlib import Path
from uuid import uuid4

import pytest
from PySide6 import QtWidgets
from pytest import MonkeyPatch
from pytestqt.qtbot import QtBot

from aims.managers.data_manager import DataManager
from aims.managers.windows_manager.windows.main_window import MainWindow
from tests.fakes.settings import FakeSettings


class FakeApplication:

    def __init__(self):
        self.is_reseted = False
        self.is_forced = None

    def reset(self, force: bool):
        self.is_reseted = True
        self.is_forced = force


def fake_file_dialog(path: str):

    @wraps(fake_file_dialog)
    def wrapper(
        self,
        parent: QtWidgets.QWidget,
        caption: str,
        dir: str,  # noqa: A002
    ) -> str:
        return path

    return wrapper


def test_cancel_pressed(
    data_manager: DataManager,
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
    qtbot: QtBot,
):
    directory = str(tmp_path)
    fake_settings = FakeSettings(
        data={'config/directory': directory},
    )
    monkeypatch.setattr('aims.managers.windows_manager.windows.main_window.get_setting', fake_settings.get_settings)
    monkeypatch.setattr(QtWidgets.QFileDialog, 'getExistingDirectory', fake_file_dialog(
        path='',
    ))
    main_window = MainWindow(
        data_manager=data_manager,
    )

    main_window.on_directory_opened()

    assert fake_settings.data['config/directory'] == directory


def test_same_path_selected(
    data_manager: DataManager,
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
    qtbot: QtBot,
):
    directory = str(tmp_path)
    fake_settings = FakeSettings(
        data={'config/directory': directory},
    )
    monkeypatch.setattr('aims.managers.windows_manager.windows.main_window.get_setting', fake_settings.get_settings)
    monkeypatch.setattr(QtWidgets.QFileDialog, 'getExistingDirectory', fake_file_dialog(
        path=directory,
    ))
    main_window = MainWindow(
        data_manager=data_manager,
    )

    main_window.on_directory_opened()

    assert fake_settings.data['config/directory'] == directory


@pytest.mark.skip()
def test_new_path_selected(
    data_manager: DataManager,
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
    qtbot: QtBot,
):
    old_directory = str(tmp_path)
    new_directory = str(tmp_path / str(uuid4()))
    fake_settings = FakeSettings(
        data={'config/directory': old_directory},
    )
    monkeypatch.setattr('aims.managers.windows_manager.windows.main_window.get_setting', fake_settings.get_settings)
    monkeypatch.setattr('aims.managers.windows_manager.windows.main_window.set_setting', fake_settings.set_settings)
    monkeypatch.setattr(QtWidgets.QFileDialog, 'getExistingDirectory', fake_file_dialog(
        path=new_directory,
    ))
    main_window = MainWindow(
        data_manager=data_manager,
    )

    main_window.on_directory_opened()

    assert fake_settings.data['config/directory'] == new_directory


@pytest.mark.skip()
def test_on_open_triggered_by_shortcut(
    data_manager: DataManager,
    monkeypatch: MonkeyPatch,
    qtbot: QtBot,
):
    monkeypatch.setattr(QtWidgets.QFileDialog, 'getExistingDirectory', fake_file_dialog)

    main_window = MainWindow(
        data_manager=data_manager,
    )

    qtbot.keySequence(main_window, 'Ctrl+O')

    assert isinstance(main_window, MainWindow)
