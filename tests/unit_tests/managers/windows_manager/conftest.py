import os
import sys

import pytest

import aims
from aims.managers.data_manager import DataManager


@pytest.fixture
def data_manager():
    return DataManager()


@pytest.fixture(autouse=True)
def setdefault_environ() -> None:
    os.environ['APPLICATION_NAME'] = 'AIMS'
    os.environ['APPLICATION_VERSION'] = aims.__version__
    os.environ['ORGANIZATION_NAME'] = aims.__organization__

    os.environ['DEPLOY'] = str(hasattr(sys, '_MEIPASS'))
