import sys

from aims.app import Application
from aims.configs import setdefault_config
from aims.environs import setdefault_environ
from aims.loggers import setdefault_logger
from aims.settings import setdefault_setting


if __name__ == '__main__':

    # setup env
    setdefault_environ()

    # config
    setdefault_config()

    # setting
    setdefault_setting()

    # logging
    setdefault_logger()

    # app
    app = Application(sys.argv)
    app.run()

    # exit
    sys.exit(app.exec())
