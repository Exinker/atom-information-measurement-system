import os

from PySide6 import QtCore, QtGui, QtWidgets

import aims
from aims.config import WIDGET_IS_ENABLE
from aims.managers.data_manager import DataManager
from aims.managers.windows_manager.widgets.centralWidget import CentralWidget
from aims.managers.windows_manager.windows.widgetWindow import WidgetWindow
from aims.settings import get_setting, set_setting

from spectrumapp.decorators import wait
from spectrumapp.helpers import find_action, find_window
from spectrumapp.loggers import log
from spectrumapp.windows.mainWindow import BaseMainWindow
from spectrumapp.windows.splashScreenWindow import splashscreen


class MainWindow(BaseMainWindow):

    # @splashscreen(progress=70, info='<strong>LOADING</strong> user interface...')
    def __init__(self, *args, data_manager: DataManager, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_manager = data_manager

        # main window
        self.setCentralWidget(
            CentralWidget(
                data_manager=self.data_manager,
                parent=self,
            ),
        )

        # update title
        self._update_title()

        # widget window
        self.widgetWindow = WidgetWindow()

        # actions
        if WIDGET_IS_ENABLE:
            action = QtGui.QAction('&Open Info', self)
            action.setEnabled(True)
            action.setCheckable(True)
            action.setChecked(get_setting('widgetWindow/visible'))
            action.setShortcut('Ctrl+I')
            action.setShortcutContext(QtCore.Qt.ApplicationShortcut)
            action.toggled.connect(self._on_show_widget_window_triggered)
            self.addAction(action)

    # --------        slots        --------
    @log(message='window: open action')
    @wait
    def _on_open_triggered(self):
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

        # update setting
        set_setting(
            key='config/directory',
            value=path,
        )

        # reset app
        app.reset(force=True)

    @log(message='window: refresh action')
    @wait
    def _on_refresh_triggered(self, *args, **kwargs):
        app = QtWidgets.QApplication.instance()

        # visible
        if (not get_setting(key='mainWindow/visible')) and (not get_setting(key='widgetWindow/visible')):
            visible = True
        else:
            visible = get_setting(key='mainWindow/visible')

        self.setVisible(visible)

        # update title
        self._update_title()

        # menus
        menubar = self.menuBar()
        menubar.setVisible(get_setting(key='mainWindow/menubar'))

        # update app windows
        for window in app.topLevelWidgets():
            window_name = window.objectName()

            if window_name in ['mainWindow']:
                window.centralWidget()._on_refresh_triggered()

            if window_name in ['HelpWindow', 'AboutWindow']:
                pass

    @log(message='window: reset action')
    @wait
    @splashscreen(delay=1)
    def _on_reset_triggered(self, *args, **kwargs):
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

    @log(message='window: show/hide widget action')
    @wait
    def _on_show_widget_window_triggered(self):
        action = find_action(self, text='&Open Info')
        visible = action.isChecked()

        set_setting(
            key='widgetWindow/visible',
            value=visible,
        )

        # refresh info window
        window = find_window('widgetWindow')
        window._on_refresh_triggered()

    def _update_title(self) -> None:

        title = get_title(
            data_manager=self.data_manager,
        )
        self.setWindowTitle(title)


def get_title(
    data_manager: DataManager,
) -> str:

    if not data_manager.data:
        return '{application_name} {application_version}'.format(
            application_name=aims.__name__,
            application_version=aims.__version__,
        )

    datum = data_manager.last_datum
    return '{application_name} {application_version} - [{analysis_name} / {probe_name}] - [{datetime_updated}]'.format(
        application_name=aims.__name__,
        application_version=aims.__version__,
        analysis_name=datum.meta.analysis_name,
        probe_name=datum.meta.probe_name,
        datetime_updated=data_manager.milestone.strftime('%Y-%m-%d %H:%M:%S'),
    )
