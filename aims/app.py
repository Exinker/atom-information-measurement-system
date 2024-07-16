import logging
import os
from datetime import datetime

from PySide6 import QtCore, QtWidgets

from spectrumapp.loggers import log
from spectrumapp.utils.handler import wait
from spectrumapp.windows.splashScreenWindow import splashscreen

import aims
from aims.config import Config
from aims.core.data import fetch_data
from aims.core.observer import Observer, ObserverEventHandler
from aims.core.setting import get_setting
from aims.window.mainWindow import MainWindow


try:  # change app id for correct icon present
    from PySide6.QtWinExtras import QtWin

    app_id = f'{aims.__organization__}.{aims.__name__}.MAINWINDOW.{aims.__version__}'
    QtWin.setCurrentProcessExplicitAppUserModelID(app_id)

except ImportError:
    pass


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

    @splashscreen(progress=50, info='<strong>PARSING</strong> xml files...')
    def _update_data(self) -> None:
        """Update (or parse) tracked path data."""

        self.data = fetch_data(
            milestone=self.milestone,
            config=Config.load(),
        )

    def _update_window(self) -> None:
        self.window._onRefreshTriggered()

    @splashscreen(progress=10, info='<strong>LOADING</strong> interface...')
    def _setup_window(self, *args, **kwargs) -> None:
        self.window = MainWindow(
            flags=QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint,
        )

    @splashscreen(progress=30, info='<strong>SETTING</strong> a watcher...')
    def _setup_observer(self) -> None:
        """Setup tracked path observer."""

        # observer's handler
        handler = ObserverEventHandler(callback=self.reset, logger=logging.getLogger('app'))

        # observer's path
        path = os.path.abspath(
            path=get_setting('config/directory'),
        )

        # setup observer
        observer = Observer()
        observer.schedule(handler, path=path, recursive=True)
        observer.start()

        # update (if needed) current observer
        if self.observer is not None:
            self.observer.stop()

        self.observer = observer

    # --------        slots        --------
    @splashscreen()
    @wait
    def run(self, *args, **kwargs):
        """Run an application."""

        self._setup_window()

        #
        self.reset(force=True)

    @log(message='app: reset')
    @splashscreen()
    @wait
    def reset(self, *args, force: bool = False, **kwargs):
        """Reset an application: update observer (if `force == True`), data and windows."""

        if force:
            self._setup_observer()

        self._update_milestone()
        self._update_data()
        self._update_window()
