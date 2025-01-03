import os
import sys

import pytest

import aims


@pytest.fixture(scope='session', autouse=True)
def setup_environ():
    os.environ['APPLICATION_NAME'] = 'AIMS'
    os.environ['APPLICATION_VERSION'] = aims.__version__
    os.environ['ORGANIZATION_NAME'] = aims.__organization__

    os.environ['DEPLOY'] = str(hasattr(sys, '_MEIPASS'))
