import logging
import time

from PySide6 import QtWidgets

import aims
from aims.managers.data_manager import DataManager
from aims.managers.watcher_manager import WatcherManager
from aims.managers.windows_manager import WindowsManager
from aims.settings import get_setting
from spectrumapp.decorators import wait
from spectrumapp.loggers import log


try:  # change `app_id` for correct icon present
    from PySide6.QtWinExtras import QtWin

    app_id = f'{aims.__organization__}.{aims.__name__}.MAINWINDOW.{aims.__version__}'
    QtWin.setCurrentProcessExplicitAppUserModelID(app_id)
except ImportError:
    pass


LOGGER = logging.getLogger('app')


class Application(QtWidgets.QApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_manager = DataManager()
        self.watcher_manager = WatcherManager(
            data_manager=self.data_manager,
            callback=self.reset,
        )
        self.windows_manager = WindowsManager(
            data_manager=self.data_manager,
        )

        #
        self.setOrganizationName(aims.__organization__)
        self.setApplicationName(aims.__name__)
        self.setApplicationVersion(aims.__version__)

    @wait
    def run(self, *args, **kwargs):
        """Run an application."""

        self.watcher_manager.setup(
            path=get_setting('config/directory'),
        )
        self.windows_manager.setup()

        self.update()

    @log(message='app: reset')
    @wait
    def reset(self, force: bool = False):

        if force:
            self.watcher_manager.setup(
                path=get_setting('config/directory'),
            )
            self.data_manager.clear()

        self.update()

    @log(message='app: update')
    @wait
    def update(self):
        started_at = time.perf_counter()

        self.data_manager.update()
        self.windows_manager.update()

        LOGGER.info('Update app elapsed time: %s, s.', time.perf_counter() - started_at)
