import dataclasses
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import pandas as pd

from spectrumapp.exception import eprint

from src import APPLICATION_VERSION


# ---------        CONSTANTS        ---------
DEBUG = True
DEPLOY = hasattr(sys, '_MEIPASS')

# ---------        EXPLORER        ---------
match sys.platform:
    case 'win32':
        EXPLORER = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
    case _:
        EXPLORER = ''


# ---------        CONFIG PARAMS        ---------
class Mode(Enum):
    CONVERGENCE = 'convergence-control'
    REFERENCE = 'reference-control'
    NONE = 'none'

    @classmethod
    def default(cls) -> 'Mode':
        return cls.CONVERGENCE

    @classmethod
    def from_str(cls, value: str) -> 'Mode':

        valid_values = {item.value: item for item in cls}
        if value in valid_values:
            return valid_values[value]

        message = 'Tracked mode {mode} is not supported! Select from: {modes}.'.format(
            mode=json.dumps(value),
            modes=', '.join(map(json.dumps, valid_values)),
        )
        raise ValueError(message)


class TrackedPath(str):

    @classmethod
    def default(cls) -> 'TrackedPath':
        path = os.getcwd()

        super_path, root_dirname = os.path.split(path)
        database_dir = os.path.join(super_path, 'DB')

        # check root directory
        if root_dirname.upper() != 'AIMS':
            return path

        # check database directory
        if not os.path.isdir(database_dir):
            return path

        #
        return database_dir

    def __new__(cls, path: str):

        if not os.path.exists(path):
            message = 'Tracked path {path} is not found or not available!'.format(
                path=json.dumps(path),
            )
            raise ValueError(message)

        if not os.path.isdir(path):
            message = 'Tracked path {path} have to be a directory!'.format(
                path=json.dumps(path),
            )
            raise ValueError(message)

        return super().__new__(cls, path)


class TrackedPediod(Enum):
    ALL = 'all'
    YEAR = 'year'
    MONTH = 'month'
    WEEK = 'week'
    DAY = 'day'
    TODAY = 'today'

    def check(self, value: datetime, ref: datetime | None = None) -> bool:
        ref = ref or datetime.now()  # TODO: synchronize with app now datetime!

        if self == TrackedPediod.ALL:
            return True

        if self == TrackedPediod.YEAR:
            return value > (ref - pd.offsets.DateOffset(years=1))

        if self == TrackedPediod.MONTH:
            return value > (ref - pd.offsets.DateOffset(months=1))

        if self == TrackedPediod.WEEK:
            return value > (ref - pd.offsets.DateOffset(days=1))

        if self == TrackedPediod.DAY:
            return value > (ref - pd.offsets.DateOffset(days=1))

        if self == TrackedPediod.TODAY:
            return value.date() == ref.date()

        raise ValueError(f'Tracked pediod {self} is not supported!.')

    @classmethod
    def default(cls) -> 'TrackedPediod':
        return cls.TODAY

    @classmethod
    def from_str(cls, value: str) -> 'TrackedPediod':

        valid_values = {item.value: item for item in cls}
        if value in valid_values:
            return valid_values[value]

        message = 'Tracked pediod {value} is not supported! Select from: {valid_values}.'.format(
            value=json.dumps(value),
            valid_values=', '.join(map(json.dumps, valid_values)),
        )
        raise ValueError(message)


class TrackedQueue(int):

    def __new__(cls, value: int):

        if not isinstance(value, int):
            message = 'Tracked queue length {value} have to be integer!'.format(
                value=json.dumps(value),
            )
            raise ValueError(message)

        if not (1 <= value <= 10):
            message = 'Tracked queue length {value} have to be in [1; 10] interval!'.format(
                value=json.dumps(value),
            )
            raise ValueError(message)

        return super().__new__(cls, value)


class FiltratedSheet:

    def __new__(cls, value: str | None):

        # no separation
        if value is None:
            return None

        #
        if not isinstance(value, str):
            message = 'Filtrated sheet "{value}" have to be "null" or string!'.format(
                value=json.dumps(value),
            )
            raise ValueError(message)

        if value == '':
            message = 'Filtrated sheet "{value}" have to be NOT empty string!'.format(
                value=json.dumps(value),
            )
            raise ValueError(message)

        return value


class FiltratedLabel(Enum):
    LABORANT = 'laborant'
    ENGINEAR = 'enginear'
    REPORT = 'report'
    NONE = 'none'

    @classmethod
    def default(cls) -> 'FiltratedLabel':
        return cls.NONE

    @classmethod
    def from_str(cls, value: str) -> 'TrackedPediod':

        #
        valid_values = {item.value: item for item in cls}
        if value in valid_values:
            return valid_values[value]

        message = 'Filtrated label {value} is not supported! Select from: {valid_values}.'.format(
            value=json.dumps(value),
            valid_values=', '.join(map(json.dumps, valid_values)),
        )
        raise ValueError(message)


class Separator:
    """Probe's name separation symbol."""

    def __new__(cls, value: str | None):

        # no separation
        if value is None:
            return None

        #
        if not isinstance(value, str):
            message = 'Separator value "{value}" have to be "null" or string!'.format(
                value=json.dumps(value),
            )
            raise ValueError(message)

        if value == '':
            message = 'Separator value have "{value}" to be NOT empty string!'.format(
                value=json.dumps(value),
            )
            raise ValueError(message)

        return value


class DatabasePath(str):

    def __new__(cls, path: str | None):

        # no database
        if path is None:
            return None

        #
        if not os.path.exists(path):
            message = 'Database path {path} is not found or not available!'.format(
                path=json.dumps(path),
            )
            raise ValueError(message)

        if not (os.path.isfile(path) and path.endswith('.xml')):
            message = 'Database path {path} have to be a path of `xml` file!'.format(
                path=json.dumps(path),
            )
            raise ValueError(message)

        return super().__new__(cls, path)


# ---------        Config        ---------
@dataclass(frozen=True)
class Config():
    version: str
    mode: Mode

    tracked_path: TrackedPath
    tracked_period: TrackedPediod
    tracked_analisys: str = field(default='')
    tracked_probe: str = field(default='')
    tracked_queue: int = field(default=5)

    filtrated_by_sheet: FiltratedSheet = field(default=None)
    filtrated_by_label: FiltratedLabel = field(default=FiltratedLabel.default())

    sep: str = field(default='*')

    database_path: DatabasePath = field(default=DatabasePath(None))

    @classmethod
    def default(cls, save: bool = False) -> 'Config':
        """Generate default config file."""

        config = cls(
            version=APPLICATION_VERSION,
            mode=Mode.default(),
            tracked_path=TrackedPath.default(),
            tracked_period=TrackedPediod.default(),
        )

        #
        if save:
            config.to_json()

        #
        return config

    @classmethod
    def update(cls, key: str, value: Any, filepath: str | None = None) -> None:
        """Update config file."""

        if filepath is None:
            filepath = os.path.join('.', 'config.json')

        # load
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # update
        data[key] = value

        # dump
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file)

    def to_json(self, filepath: str | None = 'config.json') -> None:
        """Pull config to json."""

        # serialize data
        data = {}
        for key, value in dataclasses.asdict(self).items():
            if isinstance(value, Enum):
                value = value.value

            data[key] = value

        # dump data
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file)

    @classmethod
    def from_json(cls, filepath: str | None = None) -> 'Config':
        """Push config from json."""

        if filepath is None:
            filepath = os.path.join('.', 'config.json')

        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)

                #
                config = Config(
                    version=data['version'],
                    mode=Mode.from_str(value=data['mode']),

                    tracked_path=TrackedPath(path=data['tracked_path']),
                    tracked_period=TrackedPediod.from_str(value=data['tracked_period']),
                    tracked_analisys=data['tracked_analisys'],
                    tracked_probe=data['tracked_analisys'],
                    tracked_queue=TrackedQueue(value=data['tracked_queue']),

                    filtrated_by_sheet=data['filtrated_by_sheet'],
                    filtrated_by_label=FiltratedLabel.from_str(value=data['filtrated_by_label']),

                    sep=Separator(value=data['sep']),

                    database_path=DatabasePath(path=data['database_path']),
                )

        except (json.JSONDecodeError, TypeError, ValueError, KeyError):
            eprint(msg='config: from_json')
            config = cls.default(save=True)

        return config


def setdefault_config() -> None:
    """Generate default config file if needed."""

    if not os.path.exists('config.json'):
        Config.default(save=True)
