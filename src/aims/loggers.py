import logging
import logging.config
import os

from PySide6 import QtGui, QtWidgets

from aims.config import (
    LOGGING_LEVEL,
    LOGGING_MAX_BYTES,
)
from spectrumapp.helpers import find_window
from spectrumapp.windows.progress_window import ProgressWindow


class ProgressWindowHandler(logging.StreamHandler):

    WINDOW_NAME = 'progressWindow'

    def __init__(self):
        super().__init__(self)

    def emit(self, record):

        return None

        if record.msg != 'Parse XML: %r':
            return None

        window = find_window(self.WINDOW_NAME)
        if window is not None:
            window.show()
        else:
            window = ProgressWindow()

        widget = window.findChild(QtWidgets.QPlainTextEdit, 'loggingPlainText')
        widget.moveCursor(QtGui.QTextCursor.End)
        widget.appendHtml(f'\t{record.message}')

        window.show()

        self.flush()


def setdefault_logger():

    config = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'file_formatter': {
                'format': '[%(asctime)s.%(msecs)04d] %(levelname)-8s %(module)s - %(message)s',
            },
            'progress_window_formatter': {
                'format': '%(message)s',
            },
        },

        'handlers': {
            'stream_handler': {
                'class': 'logging.StreamHandler',
                'level': logging.DEBUG,
                'formatter': 'file_formatter',
            },
            'file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': LOGGING_LEVEL,
                'formatter': 'file_formatter',
                'filename': os.path.join('.', 'app.log'),
                'mode': 'a',
                'maxBytes': LOGGING_MAX_BYTES,
                'backupCount': 3,
                'encoding': 'utf-8',
            },
            'progress_window_handler': {
                'class': 'aims.loggers.ProgressWindowHandler',
                'level': logging.DEBUG,
                'formatter': 'progress_window_formatter',
            },
        },

        'loggers': {
            'app': {
                'level': logging.DEBUG,
                'handlers': [
                    'stream_handler',
                    'file_handler',
                    'progress_window_handler',
                ],
                'propagate': True,
            },
            'spectrumapp': {
                'level': logging.DEBUG,
                'handlers': [
                    'file_handler',
                    'stream_handler',
                ],
                'propagate': True,
            },
        },
    }
    logging.config.dictConfig(config)
