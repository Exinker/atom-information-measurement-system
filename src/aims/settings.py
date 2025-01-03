
import json
import os
from enum import Enum
from typing import Any

from PySide6 import QtCore

from spectrumapp.loggers import log
from spectrumapp.settings import load_settings

from aims.config import Config


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
    FILTER_LEVEL = 'filter-level'

    @classmethod
    def is_in(cls, item) -> bool:
        return item in cls._member_names_


# ---------        settings        ---------
@log(message='setting: get')
def get_setting(key: str) -> Any:

    match key.split('/'):
        case 'config', key:
            config = Config.load()

            if key == 'directory':
                return os.path.abspath(config.directory)
            if key == 'tracked_queue_length':
                return config.tracked_queue_length

            raise ValueError(f'key {key} is not supported!')

        case 'table', key:
            settings = load_settings()
            value = settings.value('table/{}'.format(key))

            if key in ['n_rows', 'n_columns']:
                try:
                    return int(value)
                except Exception:
                    return 1

            if key == 'sorter-kind':
                if SorterKind.is_in(value):
                    return SorterKind[value]
                return SorterKind['NONE']

            if key == 'filter-level':
                if FilterLevel.is_in(value):
                    return FilterLevel[value]
                return FilterLevel['NOTSET']

        case _:
            settings = load_settings()
            value = settings.value(key)

            try:
                return json.loads(value)
            except Exception:
                return value


@log(message='setting: set')
def set_setting(key: str, value: str | int | float | list) -> None:

    match key.split('/'):
        case 'config', key:
            config = Config.load()
            config.update({key: value})

        case _:
            settings = load_settings()
            settings.setValue(key, value)
            settings.sync()


def setdefault_setting() -> None:

    # setdefault settings.ini
    if not os.path.exists('settings.ini'):
        settings = QtCore.QSettings('settings.ini', QtCore.QSettings.IniFormat)

        settings.setValue('mainWindow/visible', True)
        settings.setValue('mainWindow/menubar', False)
        settings.setValue('mainWindow/queue-widget', True)
        settings.setValue('mainWindow/meta-widget', False)

        settings.setValue('widgetWindow/visible', False)

        settings.setValue('table/n_rows', 1)
        settings.setValue('table/n_columns', 10)
        settings.setValue('table/filter-level', FilterLevel.NOTSET.name)
        settings.setValue('table/sorter-kind', SorterKind.NONE.name)

        settings.sync()

    # setdefault config
    if not os.path.exists('config.json'):
        config = Config.default()
        config.dump()
