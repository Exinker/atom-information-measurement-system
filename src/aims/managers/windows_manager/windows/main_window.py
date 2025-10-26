import os

from PySide6 import QtWidgets

import aims
from aims.managers.data_manager import DataManager
from aims.managers.windows_manager.widgets.central_widget import CentralWidget
from aims.managers.windows_manager.windows.widget_window import WidgetWindow
from aims.settings import get_setting, set_setting
from spectrumapp.loggers import log
from spectrumapp.windows.main_window import BaseMainWindow
from spectrumapp.windows.modifiers import wait
from spectrumapp.windows.splash_screen_window import utils


class MainWindow(BaseMainWindow):

    # @utils.splashscreen(progress=70, info='<strong>LOADING</strong> user interface...')
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
        self.on_title_updated()

        # widget window
        self.widgetWindow = WidgetWindow()

    @log(message='window: refresh action')
    @wait
    def on_refreshed(self, *args, **kwargs):
        app = QtWidgets.QApplication.instance()

        # visible
        if all([
            not get_setting(key='mainWindow/visible'),
            not get_setting(key='widgetWindow/visible'),
        ]):
            visible = True
        else:
            visible = get_setting(key='mainWindow/visible')

        self.setVisible(visible)

        # update title
        self.on_title_updated()

        # menus
        menubar = self.menuBar()
        menubar.setVisible(get_setting(key='mainWindow/menubar'))

        # update app windows
        for window in app.topLevelWidgets():
            window_name = window.objectName()

            if window_name in ['mainWindow']:
                window.centralWidget().on_refreshed()

            if window_name in ['HelpWindow', 'AboutWindow']:
                pass

    @log(message='window: reset action')
    @wait
    @utils.splashscreen(delay=1)
    def on_resetted(self, *args, **kwargs):
        '''An action occurs due to change file.'''
        app = QtWidgets.QApplication.instance()

        # reset app
        app.reset(force=True)

        # update title
        self.on_title_updated()

        # reset windows
        for window in app.topLevelWidgets():
            window_name = window.objectName()

            if window_name in ['mainWindow']:
                pass
            else:
                window.close()

    @log(message='window: open action')
    @wait
    def on_directory_opened(self, *args, **kwargs):
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

    def on_title_updated(self) -> None:

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
