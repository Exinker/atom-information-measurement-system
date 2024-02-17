"""
TODO:
    - Настройка количества значащих цифр (не больше, чем в XML-файле);

TIMEIT:
    2023.04.10 - 3 days
    2023.04.17 - 1 day
    2023.04.24 - 5 days
    2023.05.02 - 3 days
    2023.06.05 - 3 days
    2023.06.12 - 2 days
    2023.06.19 - 3 days
    2023.09.11 - 1 days
"""

import logging
import os
import sys
from datetime import datetime

from PySide6 import QtCore, QtWidgets

from spectrumapp.core.logging import log, setdefault_logging
from spectrumapp.utils.find import find_window
from spectrumapp.utils.modifier import wait
from spectrumapp.window.splashScreenWindow import splashscreen
from spectrumapp.window.window import BaseMainWindow

from src import APPLICATION_NAME, APPLICATION_VERSION, ORGANIZATION_NAME
from src.core.config import DEBUG, Config, setdefault_config
from src.core.data import fetch_data
from src.core.observer import Observer, ObserverEventHandler
from src.core.setting import get_setting, set_setting, setdefault_setting
from src.widget.analisysWidget import AnalysisWidget
from src.widget.metaWidget import MetaWidget
from src.widget.probeWidget import ProbeWidget
from src.window.widgetWindow import WidgetWindow


try:  # change app id for correct icon present
    from PySide6.QtWinExtras import QtWin

    app_id = f'{ORGANIZATION_NAME}.{APPLICATION_NAME}.MAINWINDOW.{APPLICATION_VERSION}'
    QtWin.setCurrentProcessExplicitAppUserModelID(app_id)

except ImportError:
    pass


class CentralWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent=parent)

        # layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        #
        self.stackedWidget = QtWidgets.QStackedWidget(parent=self)
        layout.addWidget(self.stackedWidget)

        self.probeWidget = ProbeWidget(parent=self)
        self.stackedWidget.addWidget(self.probeWidget)

        self.analysisWidget = AnalysisWidget(parent=self)
        self.stackedWidget.addWidget(self.analysisWidget)

        #
        self.metaWidget = MetaWidget(
            parent=self,
        )
        layout.addWidget(self.metaWidget)

    # --------        slots        --------
    def _onRefreshAction(self):

        # update current widget
        widget = self.analysisWidget if get_setting(key='mainWindow/queue-widget') else self.probeWidget
        widget._onRefreshAction()

        # update stacked widget
        self.stackedWidget.setCurrentWidget(widget)

        # update info widget
        self.metaWidget._onRefreshAction()


class MainWindow(BaseMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # main window
        self.setCentralWidget(
            CentralWidget(parent=self)
        )

        # info window
        self.widgetWindow = WidgetWindow()

        # actions
        self._setdefault_actions()

        # action = QtGui.QAction('&Open Info', self)
        # action.setEnabled(True)
        # action.setCheckable(True)
        # action.setChecked(get_setting('widgetWindow/visible'))
        # action.setShortcut('Ctrl+Shift+I')
        # action.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        # action.toggled.connect(self._onOpenInfoWindowAction)
        # self._add_action(action, 'open-info-window')

        # menubar
        menubar = self.menuBar()
        menubar.setVisible(get_setting(key='mainWindow/menubar'))
        self._setdefault_menubar()

    # --------        slots        --------
    @log(msg='window: open', debug=DEBUG)
    @wait
    def _onOpenAction(self):
        app = QtWidgets.QApplication.instance()

        # update path
        path = QtWidgets.QFileDialog().getExistingDirectory(
            parent=self,
            caption='Выберете каталог:',
            dir=get_setting(key='config/tracked_path'),
        )
        path = os.sep.join(path.split('/'))

        if path == '':
            return
        if path == get_setting(key='config/tracked_path'):
            return

        # update: setting
        set_setting(
            key='config/tracked_path',
            value=path,
        )

        # update: app
        app.reset(force=True)

    @log(msg='app: reset action', debug=DEBUG)
    @wait
    # @splashscreen(delay=1)
    def _onResetAppAction(self, *args, **kwargs):
        '''An action occurs due to change file.'''
        app = QtWidgets.QApplication.instance()

        # reset app
        app.reset()

        # update title
        datum = app.data.last_datum
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        title = f'{APPLICATION_NAME} - [{datum.analysis_name} / {datum.probe_name}] - [{dt}]'
        self.setWindowTitle(title)

        # reset windows
        for window in app.topLevelWidgets():
            window_name = window.objectName()

            if window_name in ('mainWindow',):
                pass
            else:
                window.close()

    @log(msg='window: refresh', debug=DEBUG)
    @wait
    def _onRefreshAppAction(self, *args, **kwargs):
        app = QtWidgets.QApplication.instance()

        # visible
        if (not get_setting(key='mainWindow/visible')) and (not get_setting(key='widgetWindow/visible')):
            visible = True
        else:
            visible = get_setting(key='mainWindow/visible')

        self.setVisible(visible)

        # update window: title
        datum = app.data.last_datum
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        title = f'{APPLICATION_NAME} - [{datum.analysis_name} / {datum.probe_name}] - [{dt}]' if datum else f'{APPLICATION_NAME} - [{dt}]'
        self.setWindowTitle(title)

        # update app windows
        for window in app.topLevelWidgets():
            window_name = window.objectName()

            if window_name in ('mainWindow',):
                window.centralWidget()._onRefreshAction()

            if window_name in ('widgetWindow',):
                window._onRefreshAction()

            if window_name in ('HelpWindow', 'AboutWindow', ):
                pass

    def _onOpenInfoWindowAction(self):
        action = self._actions['open-info-window']
        visible = action.isChecked()

        #
        set_setting(
            key='widgetWindow/visible',
            value=visible,
        )

        # refresh info window
        window = find_window('widgetWindow')
        window._onRefreshAction()


class Application(QtWidgets.QApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setOrganizationName(ORGANIZATION_NAME)
        self.setApplicationName(APPLICATION_NAME)
        self.setApplicationVersion(APPLICATION_VERSION)

        self.data = None
        self.window = None
        self.observer = None

    # --------        slots        --------
    # @splashscreen(progress=10, info='<strong>LOADING</strong> user_name interface...')
    def _setup_window(self, *args, **kwargs) -> None:
        self.window = MainWindow(
            flags=QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint,
        )

    def _update_window(self) -> None:
        self.window._onRefreshAppAction()

    # @splashscreen(progress=30, info='<strong>SETTING</strong> a watcher...')
    def _setup_observer(self) -> None:
        """Setup tracked path observer."""

        # observer's handler
        handler = ObserverEventHandler(callback=self.reset, logger=logging.getLogger('app'))

        # observer's path
        path = os.path.abspath(
            path=get_setting('config/tracked_path'),
        )

        # setup observer
        observer = Observer()
        observer.schedule(handler, path=path, recursive=True)
        observer.start()

        # update (if needed) current observer
        if self.observer is not None:
            self.observer.stop()

        self.observer = observer

    # @splashscreen(progress=50, info='<strong>PARSING</strong> xml files...')
    def _update_data(self) -> None:
        """Update (or parse) tracked path data."""

        self.data = fetch_data(
            config=Config.from_json(),
        )

    # --------        slots        --------
    # @splashscreen()
    @wait
    def run(self, *args, **kwargs):
        """Run an application."""

        self._setup_window()

        #
        self.reset(force=True)

    @log(msg='app: reset', debug=DEBUG)
    # @splashscreen()
    @wait
    def reset(self, *args, force: bool = False, **kwargs):
        """Reset an application: update observer (if `force == True`), data and windows."""

        if force:
            self._setup_observer()

        self._update_data()
        self._update_window()


if __name__ == '__main__':

    # config
    setdefault_config()

    # setting
    setdefault_setting()

    # logging
    setdefault_logging()

    # app
    app = Application(sys.argv)
    app.run()

    # exit
    sys.exit(app.exec())
