import logging
import logging.config
import os

from PySide6 import QtGui

from aims.config import LOGGING_LEVEL
from spectrumapp.utils import find_window
# from spectrumapp.windows.splashScreenWindow import splashscreen


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

        # flush
        self.flush()


# @splashscreen(progress=0, info='<strong>SET DEFAULT</strong> logging...')
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
            'file_handler': {
                'class': 'logging.FileHandler',
                'level': logging.NOTSET,
                'filename': os.path.join('.', 'app.log'),
                'mode': 'a',
                'formatter': 'file_formatter',
                'encoding': 'utf-8',
            },
            'stream_handler': {
                'class': 'logging.StreamHandler',
                'level': logging.NOTSET,
                'formatter': 'file_formatter',
            },
            # 'progress_window_handler': {
            #     'class': 'loggers.ProgressWindowHandler',
            #     'level': logging.INFO,
            #     'formatter': 'progress_window_formatter',
            # },
        },

        'loggers': {
            'app': {
                'level': LOGGING_LEVEL,
                'handlers': [
                    'file_handler',
                    'stream_handler',
                    # 'progress_window_handler',
                ],
                'propagate': False,
            },
        },
    }
    logging.config.dictConfig(config)
