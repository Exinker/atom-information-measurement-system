import sys

from aims import (
    Application,
    DEBUG,
    setdefault_config, setdefault_environ, setdefault_logger, setdefault_setting,
)


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
