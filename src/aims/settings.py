import json
import os
from enum import Enum
from typing import Any, Literal, Mapping, get_args

from PySide6 import QtCore

from aims.config import Config
from spectrumapp.loggers import log
from spectrumapp.settings import load_settings
from spectrumapp.types import DirPath


class FilterLevel(Enum):
    NOTSET = 0
    NORMAL = 1
    WARRING = 2
    DANGER = 3

    @classmethod
    def is_contains(cls, item: str) -> bool:
        return item in cls._member_names_


class SorterKind(Enum):
    NONE = 'none'
    FILTER_LEVEL = 'filter-level'

    @classmethod
    def is_contains(cls, item: str) -> bool:
        return item in cls._member_names_


class FontSize:
    VALUES = Literal['12', '14', '16']
    DEFAULT = '14'

    @classmethod
    def is_contains(cls, item: str) -> bool:
        return item in get_args(cls.VALUES)


class FontWeight:
    VALUES = Literal['400', '500', '600']
    DEFAULT = '400'

    @classmethod
    def is_contains(cls, item: str) -> bool:
        return item in get_args(cls.VALUES)


@log(message='setting: get')
def get_setting(key: str) -> Any:

    match key.split('/'):
        case 'config', field:
            config = Config.load()

            if field == 'directory':
                return os.path.abspath(config.directory)
            if field == 'tracked_queue_length':
                return config.tracked_queue_length

            raise ValueError(f'Field {field} is not supported!')

        case 'table', field:
            settings = load_settings()
            value = settings.value('table/{}'.format(field))

            if field in ['n_rows', 'n_columns']:
                try:
                    return int(value)
                except Exception:
                    return 1

            if field == 'sorter-kind':
                if SorterKind.is_contains(value):
                    return SorterKind[value]
                return SorterKind['NONE']

            if field == 'filter-level':
                if FilterLevel.is_contains(value):
                    return FilterLevel[value]
                return FilterLevel['NOTSET']

        case 'style', field:
            settings = load_settings()
            value = settings.value('style/{}'.format(field))

            if field == 'font-size':
                if FontSize.is_contains(value):
                    return value
                return FontSize.DEFAULT

            if field == 'font-weight':
                if FontWeight.is_contains(value):
                    return value
                return FontWeight.DEFAULT

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
            config.update(**{key: value})

        case _:
            settings = load_settings()
            settings.setValue(key, value)
            settings.sync()


DEFAULT_SETTING = {
    'mainWindow/visible': True,
    'mainWindow/menubar': False,
    'mainWindow/queue-widget': True,

    'style/font-size': FontSize.DEFAULT,
    'style/font-weight': FontWeight.DEFAULT,

    'table/n_rows': 1,
    'table/n_columns': 10,
    'table/filter-level': FilterLevel.NOTSET.name,
    'table/sorter-kind': SorterKind.NONE.name,
}


def setdefault_setting(
    filedir: DirPath | None = None,
    default_settings: Mapping[str, Any] = DEFAULT_SETTING,
) -> None:

    filedir = filedir or os.getcwd()

    # set default `settings.ini`
    filepath = os.path.join(filedir, 'settings.ini')
    if not os.path.exists(filepath):
        settings = QtCore.QSettings(filepath, QtCore.QSettings.IniFormat)

        for key, value in default_settings.items():
            settings.setValue(key, value)

        settings.sync()

    # set default `config.json`
    filepath = os.path.join(filedir, 'config.json')
    if not os.path.exists(filepath):
        Config.FILEPATH = filepath

        config = Config.default()
        config.dump()
