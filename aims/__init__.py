"""Atom Information Measurement System (AIMS)."""

from datetime import datetime

from .app import Application
from .config import DEBUG, setdefault_config
from .environs import setdefault_environ
from .loggers import setdefault_logger
from .settings import setdefault_setting


__version__ = '0.1.12'

__name__ = 'Atom Information Measurement System'
__author__ = 'Pavel Vaschenko'
__email__ = 'vaschenko@vmk.ru'
__organization__ = 'VMK-Optoelektronika'
__copyright__ = 'Copyright {}, {}'.format(datetime.now().year, __organization__)
