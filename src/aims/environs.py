import os
import sys

import aims
from aims.config import LOGGING_LEVEL


def setdefault_environ() -> None:
    os.environ['APPLICATION_NAME'] = 'AIMS'
    os.environ['APPLICATION_VERSION'] = aims.__version__
    os.environ['ORGANIZATION_NAME'] = aims.__organization__

    os.environ['DEBUG'] = str(LOGGING_LEVEL == 'DEBUG')
    os.environ['DEPLOY'] = str(hasattr(sys, '_MEIPASS'))
