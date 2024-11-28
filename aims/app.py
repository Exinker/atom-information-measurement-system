import logging
import os
import time
from datetime import datetime

from PySide6 import QtCore, QtWidgets
from watchdog.events import FileSystemEvent

import aims
from aims.config import Config
from aims.core.data import data_factory
from aims.core.parsers import CacheManager
from aims.observer import Observer, ObserverEventHandler
from aims.settings import get_setting
from aims.window.mainWindow import MainWindow
from spectrumapp.loggers import log
from spectrumapp.utils.handler import wait
# from spectrumapp.swindows.splashScreenWindow import splashscreen


try:  # change app id for correct icon present
    from PySide6.QtWinExtras import QtWin

    app_id = f'{aims.__organization__}.{aims.__name__}.MAINWINDOW.{aims.__version__}'
    QtWin.setCurrentProcessExplicitAppUserModelID(app_id)

except ImportError:
    pass


LOGGER = logging.getLogger('app')


class Application(QtWidgets.QApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setOrganizationName(aims.__organization__)
        self.setApplicationName(aims.__name__)
        self.setApplicationVersion(aims.__version__)

        self.milestone = None
        self.data = None
        self.window = None
        self.observer = None

    # --------        slots        --------
    def _update_milestone(self) -> None:
        self.milestone = datetime.now()

    # @splashscreen(progress=50, info='<strong>PARSING</strong> xml files...')
    def _update_data(self) -> None:
        """Update (or parse) tracked path sheets."""

        self.data = data_factory(
            milestone=self.milestone,
            config=Config.load(),
        )

    def _update_window(self) -> None:
        self.window._onRefreshTriggered()

    # @splashscreen(progress=10, info='<strong>LOADING</strong> interface...')
    def _setup_window(self, *args, **kwargs) -> None:
        self.window = MainWindow(
            flags=QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint,
        )

    # @splashscreen(progress=30, info='<strong>SETTING</strong> a watcher...')
    def _setup_observer(self) -> None:
        """Setup observer for tracked path."""

        self.observer = Observer()
        self.observer.schedule(
            event_handler=ObserverEventHandler(callback=self.reset),
            path=os.path.abspath(
                path=get_setting('config/directory'),
            ),
            recursive=True,
        )
        self.observer.start()

    # --------        slots        --------
    # @splashscreen()
    @wait
    def run(self, *args, **kwargs):
        """Run an application."""

        self._setup_window()

        #
        self.reset(force=True)

    @log(message='app: reset')
    # @splashscreen()
    @wait
    def reset(self, event: FileSystemEvent | None = None, force: bool = False, **kwargs):
        """Reset an application: update observer (if `force == True`), sheets and windows."""
        started_at = time.perf_counter()

        if force:
            self.observer.stop()
            self._setup_observer()

            CacheManager.clear()

        if event:
            match event.event_type:
                case 'modified':
                    CacheManager.remove(
                        filepath=event.src_path,
                    )

        self._update_milestone()
        self._update_data()
        self._update_window()
        LOGGER.info('Elapsed time: %s, s', time.perf_counter() - started_at)
