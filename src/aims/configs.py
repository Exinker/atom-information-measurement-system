import dataclasses
import json
import logging
import os
import platform
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import ClassVar, Mapping

import pandas as pd
from dotenv import load_dotenv

from spectrumapp.colors import RedOrangeYellowGreenColorset
from spectrumapp.config import (
    AbstractConfig,
    LOGGING_LEVEL_MAP,
)


load_dotenv()


LOGGER = logging.getLogger('app')


# ---------        ENV        ---------
LOGGING_LEVEL = LOGGING_LEVEL_MAP.get(os.environ.get('LOGGING_LEVEL'), logging.DEBUG)
LOGGING_MAX_BYTES = int(os.environ.get('LOGGING_MAX_BYTES', 1000 * 1000))  # 1 MByte

N_WORKERS = os.environ.get('N_WORKERS', 1)

if platform.system() == 'Windows':
    EXPLORER = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
else:
    EXPLORER = ''


# ---------        COLOR        ---------
COLOR = {
    'red': RedOrangeYellowGreenColorset.RED.value,
    'orange': RedOrangeYellowGreenColorset.ORANGE.value,
    'yellow': RedOrangeYellowGreenColorset.YELLOW.value,
    'green': RedOrangeYellowGreenColorset.GREEN.value,
    'black': 'black',
}


# ---------        CONFIG PARAMS        ---------
class Directory(str):

    @classmethod
    def default(cls) -> 'Directory':

        path = os.getcwd()

        root, name = os.path.split(path)
        if (name.upper() == 'AIMS') and os.path.isdir(os.path.join(root, 'DB')):
            return os.path.join(root, 'DB')

        return path

    def __new__(cls, path: str):

        if not os.path.isdir(path):
            message = 'Tracked path {path} have to be a directory!'.format(
                path=json.dumps(path),
            )
            raise ValueError(message)

        return super().__new__(cls, path)


class TrackedMode(Enum):
    CONVERGENCE_BY_PROBES = 'convergence-by-probes-control'
    CONVERGENCE_BY_PARALLELS = 'convergence-by-parallels-control'
    # REFERENCE = 'reference-control'

    @classmethod
    def default(cls) -> 'TrackedMode':
        return cls.CONVERGENCE_BY_PROBES

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


class TrackedPediod(Enum):
    ALL = 'all'
    YEAR = 'year'
    MONTH = 'month'
    WEEK = 'week'
    DAY = 'day'
    TODAY = 'today'

    def check(
        self,
        created_at: datetime,
        milestone: datetime | None = None,
    ) -> bool:
        milestone = milestone or datetime.now()

        match self:
            case TrackedPediod.ALL:
                return True
            case TrackedPediod.YEAR:
                return milestone < created_at + pd.offsets.DateOffset(years=1)
            case TrackedPediod.MONTH:
                return milestone < created_at + pd.offsets.DateOffset(months=1)
            case TrackedPediod.WEEK:
                return milestone < created_at + pd.offsets.DateOffset(weeks=1)
            case TrackedPediod.DAY:
                return milestone < created_at + pd.offsets.DateOffset(days=1)
            case TrackedPediod.TODAY:
                return created_at.date() == milestone.date()

        raise ValueError(f'Tracked pediod {self} is not supported!.')

    @classmethod
    def default(cls) -> 'TrackedPediod':
        return cls.ALL

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

        if value is None:
            return None

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

        if value is None:
            return None

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


# ---------        Config        ---------
DEFAULT_SEP = '*'


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

    sep: str = field(default=DEFAULT_SEP)

    FILEPATH: ClassVar[str] = field(default=os.path.join(os.getcwd(), 'config.json'))

    def dumps(self) -> Mapping[str, str | int | float | list]:
        """Serialize config to mapping object."""

        data = {}
        for key, value in dataclasses.asdict(self).items():
            if isinstance(value, Enum):
                value = value.value
            data[key] = value

        return data

    @classmethod
    def default(cls) -> 'Config':
        """Get config file by default."""

        config = cls(
            **cls._default(),
        )
        return config

    @classmethod
    def load(cls) -> 'Config':
        """Load config from file (json)."""

        try:
            data = cls._load()
        except FileNotFoundError as error:
            LOGGER.warning('Load config failed with %s: %s', type(error).__name__, error)

            setdefault_config()
            return cls.load()
        except json.JSONDecodeError as error:
            LOGGER.warning('Load config failed with %s: %s', type(error).__name__, error)

            setdefault_config(force=True)
            return cls.load()

        try:
            config = Config(
                version=data['version'],
                directory=Directory(path=data['directory']),

                tracked_mode=TrackedMode.from_str(value=data['tracked_mode']),
                tracked_period=TrackedPediod.from_str(value=data['tracked_period']),
                tracked_analisys_name=data['tracked_analisys_name'],
                tracked_probe_name=data['tracked_probe_name'],
                tracked_queue_length=TrackedQueue(value=data['tracked_queue_length']),

                filtrated_by_sheet=data['filtrated_by_sheet'],
                filtrated_by_label=FiltratedLabel.from_str(value=data['filtrated_by_label']),

                sep=Separator(value=data['sep']),
            )
        except (
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            LOGGER.warning('Load config failed with %s: %s', type(error).__name__, error)

            setdefault_config(force=True)
            return cls.load()
        else:
            return config

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

    if force or not os.path.exists(Config.FILEPATH):
        config = Config.default()
        config.dump()
