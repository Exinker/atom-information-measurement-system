import json
import logging
import os
from enum import Enum
from typing import Any, Mapping

from PySide6 import QtCore
from pydantic import BaseModel, Field, ValidationError, field_validator

from aims.configs import Config
from spectrumapp.loggers import log
from spectrumapp.settings import load_settings
from spectrumapp.types import DirPath


LOGGER = logging.getLogger('app')


class FilterLevel(Enum):
    NOTSET = 0
    NORMAL = 1
    WARRING = 2
    DANGER = 3

    @classmethod
    def validate(cls, item: str) -> bool:
        return item in cls._member_names_


class SorterKind(Enum):
    NONE = 'none'
    FILTER_LEVEL = 'filter-level'

    @classmethod
    def validate(cls, item: str) -> bool:
        return item in cls._member_names_


class BaseValidator(BaseModel):

    @classmethod
    def validate(cls, value: str | None) -> int:

        if value is None:
            return cls().value

        try:
            return cls.model_validate({'value': value}).value
        except ValidationError as error:
            LOGGER.error(
                '%s validation error: %s',
                cls.__name__,
                error,
            )
            return cls().value


class FontSize(BaseValidator):

    value: int = Field(14, ge=8, le=24)


class FontWeight(BaseValidator):

    value: int = Field(400)

    @field_validator('value')
    @classmethod
    def validate_value(cls, value: str | None) -> int:

        if value is None:
            return cls().value

        try:
            value = int(value)
            if value in [200, 400, 600]:
                return value
            raise ValueError
        except TypeError:
            raise


class HeaderHeight(BaseValidator):

    value: int = Field(20, ge=10, le=50)


class HorizontalHeaderWidth(BaseValidator):

    value: int = Field(80, ge=50, le=500)


class VerticalHeaderWidth(BaseValidator):

    value: int = Field(120, ge=50, le=500)


@log(message='setting: get', level=logging.NOTSET)
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
                if SorterKind.validate(value):
                    return SorterKind[value]
                return SorterKind['NONE']

            if field == 'filter-level':
                if FilterLevel.validate(value):
                    return FilterLevel[value]
                return FilterLevel['NOTSET']

        case 'style', field:
            settings = load_settings()
            value = settings.value('style/{}'.format(field))

            if field == 'font-size':
                return FontSize.validate(value)

            if field == 'font-weight':
                return FontWeight.validate(value)

            if field == 'header-height':
                return HeaderHeight.validate(value)

            if field == 'horizontal-header-width':
                return HorizontalHeaderWidth.validate(value)

            if field == 'vertical-header-width':
                return VerticalHeaderWidth.validate(value)

        case _:
            settings = load_settings()
            value = settings.value(key)

            try:
                return json.loads(value)
            except Exception:
                return value


@log(message='setting: set', level=logging.DEBUG)
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

    'style/font-size': FontSize().value,
    'style/font-weight': FontWeight().value,

    'table/n_rows': 1,
    'table/n_columns': 10,
    'table/filter-level': FilterLevel.NOTSET.name,
    'table/sorter-kind': SorterKind.NONE.name,
}


def setdefault_settings(
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
