import dataclasses
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import ClassVar, Mapping

import pandas as pd

from spectrumapp.config import AbstractConfig
from spectrumapp.exceptions import eprint


DEBUG = False


# ---------        EXPLORER        ---------
match sys.platform:
    case 'win32':
        EXPLORER = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
    case _:
        EXPLORER = ''


# ---------        CONFIG PARAMS        ---------
class TrackedMode(Enum):
    CONVERGENCE = 'convergence-control'
    REFERENCE = 'reference-control'
    NONE = 'none'

    @classmethod
    def default(cls) -> 'TrackedMode':
        return cls.CONVERGENCE

    @classmethod
    def from_str(cls, value: str) -> 'TrackedMode':

        valid_values = {item.value: item for item in cls}
        if value in valid_values:
            return valid_values[value]

        message = 'Tracked mode {mode} is not supported! Select from: {modes}.'.format(
            mode=json.dumps(value),
            modes=', '.join(map(json.dumps, valid_values)),
        )
        raise ValueError(message)


class Directory(str):

    @classmethod
    def default(cls) -> 'Directory':
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

    def check(self, __datetime: datetime, milestone: datetime | None = None) -> bool:
        milestone = milestone or datetime.now()

        if self == TrackedPediod.ALL:
            return True

        if self == TrackedPediod.YEAR:
            return __datetime > (milestone - pd.offsets.DateOffset(years=1))

        if self == TrackedPediod.MONTH:
            return __datetime > (milestone - pd.offsets.DateOffset(months=1))

        if self == TrackedPediod.WEEK:
            return __datetime > (milestone - pd.offsets.DateOffset(days=1))

        if self == TrackedPediod.DAY:
            return __datetime > (milestone - pd.offsets.DateOffset(days=1))

        if self == TrackedPediod.TODAY:
            return __datetime.date() == milestone.date()

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
@dataclass(frozen=True, slots=True)
class Config(AbstractConfig):
    version: str
    directory: Directory

    tracked_mode: TrackedMode
    tracked_period: TrackedPediod
    tracked_analisys_name: str = field(default='')
    tracked_probe_name: str = field(default='')
    tracked_queue_length: int = field(default=5)

    filtrated_by_sheet: FiltratedSheet = field(default=None)
    filtrated_by_label: FiltratedLabel = field(default=FiltratedLabel.default())

    sep: str = field(default='*')

    database_path: DatabasePath = field(default=DatabasePath(None))

    FILEPATH: ClassVar[str] = field(default=os.path.join(os.getcwd(), 'config.json'))

    def serialize(self) -> Mapping[str, str | int | float | list]:
        """Serialize config to mapping object."""

        data = {}
        for key, value in dataclasses.asdict(self).items():
            if isinstance(value, Enum):
                value = value.value

            data[key] = value

        #
        return data

    # ---------        factory        ---------
    @classmethod
    def default(cls) -> 'Config':
        """Get config file by default."""

        config = cls(
            **cls._default(),
        )

        #
        return config

    @classmethod
    def load(cls) -> 'Config':
        """Load config from file (json)."""

        # load data
        try:
            data = cls._load()

        except FileNotFoundError as error:
            eprint(msg=f'{cls.__name__}.load: {error}')

            setdefault_config()
            return cls.load()

        # parse data
        try:
            config = Config(
                version=data['version'],
                directory=Directory(path=data['directory']),

                tracked_mode=TrackedMode.from_str(value=data['tracked_mode']),
                tracked_period=TrackedPediod.from_str(value=data['tracked_period']),
                tracked_analisys_name=data['tracked_analisys_name'],
                tracked_probe_name=data['tracked_analisys_name'],
                tracked_queue_length=TrackedQueue(value=data['tracked_queue_length']),

                filtrated_by_sheet=data['filtrated_by_sheet'],
                filtrated_by_label=FiltratedLabel.from_str(value=data['filtrated_by_label']),

                sep=Separator(value=data['sep']),

                database_path=DatabasePath(path=data['database_path']),
            )

        except (json.JSONDecodeError, TypeError, ValueError, KeyError) as error:
            eprint(msg=f'{cls.__name__}.load: {error}')

            setdefault_config(force=True)
            return cls.load()

        #
        return config

    # ---------        private        ---------
    @classmethod
    def _default(cls) -> Mapping[str, str | int | float | list]:
        """Get default serialized data."""

        return {
            'version': os.environ['APPLICATION_VERSION'],
            'directory': Directory.default(),
            'tracked_mode': TrackedMode.default(),
            'tracked_period': TrackedPediod.default(),
        }


def setdefault_config(force: bool = False) -> None:
    """Create default config file."""

    filepath = Config.FILEPATH
    if (not os.path.exists(filepath)) or force:
        config = Config.default()
        config.dump()
