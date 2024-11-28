import sys

from aims.app import Application
from aims.config import setdefault_config
from aims.environs import setdefault_environ
from aims.loggers import setdefault_logger
from aims.settings import setdefault_setting


if __name__ == '__main__':

    setdefault_environ()
    setdefault_config()
    setdefault_setting()
    setdefault_logger()

    app = Application(sys.argv)
    app.run()
    sys.exit(app.exec())
