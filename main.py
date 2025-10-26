import sys

from aims.app import Application
from aims.configs import setdefault_configs
from aims.environs import setdefault_environ
from aims.loggers import setdefault_logger
from aims.settings import setdefault_settings


if __name__ == '__main__':

    setdefault_environ()
    setdefault_configs()
    setdefault_settings()
    setdefault_logger()

    app = Application(sys.argv)
    app.run()
    sys.exit(app.exec())
