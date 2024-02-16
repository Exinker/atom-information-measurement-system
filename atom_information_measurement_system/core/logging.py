
import logging
import logging.config
import os

from PySide6 import QtGui

from spectrumapp.utils.find import find_window
from spectrumapp.window.splashScreenWindow import splashscreen

from .config import DEBUG, DEVELOP


class ProgressWindowHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(self)

    def emit(self, record):
        message = self.format(record)

        # init window
        window_name = 'progressWindow'

        window = find_window(window_name)
        if window is not None:

            view = window.loggingPlainText
            if view:
                view.moveCursor(QtGui.QTextCursor.End)
                view.appendHtml(f'\t{message}')

            window.show()

        # # flush
        # self.flush()


# @splashscreen(progress=0, info='<strong>SET DEFAULT</strong> logging...')
def setdefault_logging():

    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'file_formatter': {
                'format': '[%(asctime)s: %(levelname)s] %(message)s',
            },
            'progress_window_formatter': {
                'format': '%(message)s',
            },
        },

        'handlers': {
            'file_handler': {
                'class': 'logging.FileHandler',
                'level': logging.DEBUG,
                'filename': os.path.join('.', 'app.log'),
                'mode': 'a',
                'formatter': 'file_formatter',
                'encoding': 'utf-8',
            },
            'progress_window_handler': {
                'class': 'core.loggings.ProgressWindowHandler',
                'level': logging.INFO,
                'formatter': 'progress_window_formatter',
            },
        },

        'loggers': {
            'app': {
                'level': logging.DEBUG,
                'handlers': ['file_handler', 'progress_window_handler'],
                'propagate': False,
            }
        }
    }
    logging.config.dictConfig(LOGGING_CONFIG)

    #
    if DEBUG or DEVELOP:
        logger = logging.getLogger('app')
        logger.debug(f'app: run')
