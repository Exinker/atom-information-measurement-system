import os
import sys

import aims


def setdefault_environ(debug: bool = False) -> None:
    os.environ['APPLICATION_NAME'] = 'AIMS'
    os.environ['APPLICATION_VERSION'] = aims.__version__
    os.environ['ORGANIZATION_NAME'] = aims.__organization__

    os.environ['DEBUG'] = str(debug)
    os.environ['DEPLOY'] = str(hasattr(sys, '_MEIPASS'))
