
import json
import os
from enum import Enum
from typing import Any

from PySide6 import QtCore

from spectrumapp.loggers import log

from aims.config import Config, DEBUG


# ---------        filtration        ---------
class FilterLevel(Enum):
    NOTSET = 0
    NORMAL = 1
    WARRING = 2
    DANGER = 3

    @classmethod
    def is_in(cls, item) -> bool:
        return item in cls._member_names_


# ---------        sorting        ---------
class SorterKind(Enum):
    NONE = 'none'
    FILTER = 'filter'

    @classmethod
    def is_in(cls, item) -> bool:
        return item in cls._member_names_


# ---------        settings        ---------
def fetch_setting() -> QtCore.QSettings:

    def inner(filepath: str) -> QtCore.QSettings:
        settings = QtCore.QSettings(filepath, QtCore.QSettings.IniFormat)
        return settings

    # fetch: setting.ini
    filedir = os.getcwd()
    filepath = os.path.join(filedir, 'setting.ini')

    return inner(filepath)


@log(message='setting: get')
def get_setting(key: str) -> Any:

    # get config values
    key_category, key_name = key.split('/')

    match key_category:
        case 'config':  # FIXME: to refactor (line dict obj)
            config = Config.load()

            if key_name == 'directory':
                return os.path.abspath(config.directory)
            if key_name == 'tracked_mode':
                return config.tracked_mode
            if key_name == 'tracked_period':
                raise NotImplementedError
            if key_name == 'tracked_probe_name':
                return config.tracked_probe_name
            if key_name == 'tracked_queue_length':
                return config.tracked_queue_length
            if key_name == 'filtrated_by_sheet':
                return config.filtrated_by_sheet
            if key_name == 'filtrated_by_label':
                return config.filtrated_by_label
            if key_name == 'sep':
                return config.sep

            raise ValueError(f'key {key} is not supported!')

        case 'filter':
            settings = fetch_setting()
            value = settings.value(key)

            return FilterLevel[value] if FilterLevel.is_in(value) else FilterLevel['NOTSET']

        case 'sorter':
            settings = fetch_setting()
            value = settings.value(key)

            return SorterKind[value] if SorterKind.is_in(value) else SorterKind['NONE']

        case _:
            settings = fetch_setting()
            value = settings.value(key)

            try:
                value = json.loads(value)
            finally:
                return value


@log(message='setting: set')
def set_setting(key: str, value: str | int | float | list) -> None:

    # update setting
    key_category, key_name = key.split('/')

    match key_category:
        case 'config':
            Config.update(
                key=key_name,
                value=value,
            )

        case _:
            settings = fetch_setting()
            settings.setValue(key, value)
            settings.sync()


def setdefault_setting() -> None:

    # setdefault setting.ini
    if not os.path.exists('setting.ini'):
        settings = QtCore.QSettings('setting.ini', QtCore.QSettings.IniFormat)

        settings.setValue('mainWindow/visible', True)
        settings.setValue('mainWindow/menubar', False)
        settings.setValue('mainWindow/queue-widget', True)
        settings.setValue('mainWindow/meta-widget', False)

        settings.setValue('widgetWindow/visible', False)

        settings.setValue('filter/level', FilterLevel.NOTSET.name)

        settings.setValue('sorter/kind', SorterKind.NONE.name)

        settings.sync()

    # setdefault config
    if not os.path.exists('config.json'):
        config = Config.default()
        config.to_json()
