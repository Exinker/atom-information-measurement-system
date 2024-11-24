import os

from PySide6 import QtWidgets

from spectrumapp.loggers import log
from spectrumapp.utils.finder import find_window
from spectrumapp.utils.handler import wait
from spectrumapp.windows.splashScreenWindow import splashscreen
from spectrumapp.windows.mainWindow import BaseMainWindow

import aims
from aims.core.data import DataABC
from aims.settings import get_setting, set_setting
from aims.widget.centralWidget import CentralWidget
from aims.window.widgetWindow import WidgetWindow


class MainWindow(BaseMainWindow):

    @splashscreen(progress=70, info='<strong>LOADING</strong> user interface...')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # main window
        self.setCentralWidget(
            CentralWidget(parent=self),
        )

        # info window
        self.widgetWindow = WidgetWindow()

        # actions
        # action = QtGui.QAction('&Open Info', self)
        # action.setEnabled(True)
        # action.setCheckable(True)
        # action.setChecked(get_setting('widgetWindow/visible'))
        # action.setShortcut('Ctrl+Shift+I')
        # action.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        # action.toggled.connect(self._onShowInfoWindowTriggered)
        # self.addAction(action)

    # --------        slots        --------
    @log(message='window: open')
    @wait
    def _onOpenTriggered(self):
        app = QtWidgets.QApplication.instance()

        # update path
        path = QtWidgets.QFileDialog().getExistingDirectory(
            parent=self,
            caption='Выберете каталог:',
            dir=get_setting(key='config/directory'),
        )
        path = os.sep.join(path.split('/'))

        if path == '':
            return
        if path == get_setting(key='config/directory'):
            return

        # update: setting
        set_setting(
            key='config/directory',
            value=path,
        )

        # update: app
        app.reset(force=True)

    @log(message='app: reset action')
    @wait
    @splashscreen(delay=1)
    def _onResetTriggered(self, *args, **kwargs):
        '''An action occurs due to change file.'''
        app = QtWidgets.QApplication.instance()

        # reset app
        app.reset(force=True)

        # update title
        self._update_title()

        # reset windows
        for window in app.topLevelWidgets():
            window_name = window.objectName()

            if window_name in ['mainWindow']:
                pass
            else:
                window.close()

    @log(message='window: refresh')
    @wait
    def _onRefreshTriggered(self, *args, **kwargs):
        app = QtWidgets.QApplication.instance()

        # visible
        if (not get_setting(key='mainWindow/visible')) and (not get_setting(key='widgetWindow/visible')):
            visible = True
        else:
            visible = get_setting(key='mainWindow/visible')

        self.setVisible(visible)

        # update window: title
        self._update_title()

        # menus
        menubar = self.menuBar()
        menubar.setVisible(get_setting(key='mainWindow/menubar'))

        # update app windows
        for window in app.topLevelWidgets():
            window_name = window.objectName()

            if window_name in ['mainWindow']:
                window.centralWidget()._onRefreshTriggered()

            if window_name in ['widgetWindow']:
                window._onRefreshTriggered()

            if window_name in ['HelpWindow', 'AboutWindow']:
                pass

    def _onShowInfoWindowTriggered(self):
        action = self._actions['open-info-window']
        visible = action.isChecked()

        #
        set_setting(
            key='widgetWindow/visible',
            value=visible,
        )

        # refresh info window
        window = find_window('widgetWindow')
        window._onRefreshTriggered()

    def _get_title(self) -> str:
        app = QtWidgets.QApplication.instance()

        if isinstance(app.data, DataABC):
            datum = app.data.last_datum

            return '{application_name} - [{analysis_name} / {probe_name}] - [{datetime_updated}]'.format(
                application_name=aims.__name__,
                analysis_name=datum.meta.analysis_name,
                probe_name=datum.meta.probe_name,
                datetime_updated=app.milestone.strftime('%Y-%m-%d %H:%M:%S'),
            )

        return '{application_name} - [{datetime_updated}]'.format(
            application_name=aims.__name__,
            datetime_updated=app.milestone.strftime('%Y-%m-%d %H:%M:%S'),
        )

    def _update_title(self) -> None:

        title = self._get_title()
        self.setWindowTitle(title)
