import sys

from aims.app import Application, setdefault_config, setdefault_logger, setdefault_setting
from aims.config import DEBUG
from aims.environ import setdefault_environ


if __name__ == '__main__':

    # setup env
    setdefault_environ(debug=DEBUG)

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
