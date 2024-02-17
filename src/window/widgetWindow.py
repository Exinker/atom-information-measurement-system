
import os

from PySide6 import QtCore, QtGui, QtWidgets

from spectrumapp.core.color import COLOR
from spectrumapp.core.utils import pave
from spectrumapp.core.setting import set_setting
from spectrumapp.utils.find import find_window
from spectrumapp.window.window import BaseWindow

from src import APPLICATION_NAME, APPLICATION_VERSION
from src.core.setting import get_setting


class LastRecordFrame(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, objectName='lastRecordFrame', **kwargs)

        #
        layout = QtWidgets.QFormLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('analysisNameValueLavel')
        layout.addRow('Анализ:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('sampleNameValueLavel')
        layout.addRow('Образец:', widget)

    # --------        slots        --------
    def _onRefreshAction(self):
        app = QtWidgets.QApplication.instance()
        datum = app.data.last_datum

        # analysisLabel
        widget = self.findChild(QtWidgets.QLabel, 'analysisNameValueLavel')
        widget.setText(
            f'{datum.analysis_name}'
        )

        # sampleNameLabel
        widget = self.findChild(QtWidgets.QLabel, 'sampleNameValueLavel')
        widget.setText(
            f'{datum.probe_name}'
        )


class StatInfoFrame(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, objectName='statInfoFrame', **kwargs)

        #
        layout = QtWidgets.QFormLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label = QtWidgets.QLabel(text='Всего:'.upper(), parent=self)
        label.setObjectName('trackedLabelLabel')
        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('trackedValueLabel')
        layout.addRow(label, widget)

        label = QtWidgets.QLabel(text='Предупреждение:'.upper(), parent=self)
        label.setObjectName('warningLabelLabel')
        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('warningValueLabel')
        layout.addRow(label, widget)

        label = QtWidgets.QLabel(text='Ошибка:'.upper(), parent=self)
        label.setObjectName('errorLabelLabel')
        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('errorValueLabel')
        layout.addRow(label, widget)

    # --------        slots        --------
    def _onRefreshAction(self):

        #
        app = QtWidgets.QApplication.instance()
        datum = app.data.last_datum
        if datum is None:
            return

        levels = datum.levels

        #
        n_columns = levels.size
        n_tracked = levels[levels > 0].size
        n_warrings = levels[levels == 2].size
        n_errors = levels[levels == 3].size

        # trackedNumberLabel
        widget = self.findChild(QtWidgets.QLabel, 'trackedValueLabel')
        widget.setText(
            f'<strong>{n_tracked}</strong>/{n_columns}'
        )

        # warningNumberLabel
        style = 'color: {color}; font-weight: {weight};'
        if n_warrings > 0:
            style = style.format(color=COLOR.get('orange', 'orange'), weight=600)
        else:
            style = style.format(color=COLOR.get('black', 'black'), weight=400)

        widget = self.findChild(QtWidgets.QLabel, 'warningLabelLabel')
        widget.setStyleSheet(style)

        widget = self.findChild(QtWidgets.QLabel, 'warningValueLabel')
        widget.setStyleSheet(style)
        widget.setText(f'{n_warrings}/{n_tracked}' if n_warrings > 0 else f'{n_warrings}')

        # errorNumberLabel
        style = 'color: {color}; font-weight: {weight};'
        if n_errors > 0:
            style = style.format(color=COLOR.get('red', 'red'), weight=600)
        else:
            style = style.format(color=COLOR.get('black', 'black'), weight=400)

        widget = self.findChild(QtWidgets.QLabel, 'errorLabelLabel')
        widget.setStyleSheet(style)

        widget = self.findChild(QtWidgets.QLabel, 'errorValueLabel')
        widget.setStyleSheet(style)
        widget.setText(f'{n_errors}/{n_tracked}' if n_errors > 0 else f'{n_errors}')


class AppInfoFrame(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, objectName='appInfoFrame', **kwargs)

        #
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(0)

        widget = QtWidgets.QLabel(parent=self, text=f'{APPLICATION_NAME.upper()}')
        widget.setObjectName('appNameLabel')
        widget.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(widget)

        widget = QtWidgets.QLabel(parent=self, text=f'VERSION {APPLICATION_VERSION}')
        widget.setObjectName('appDescriptionLabel')
        widget.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(widget)

    # --------        slots        --------
    def _onRefreshAction(self):
        pass


class WidgetWidget(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addSpacing(20)

        widget = LastRecordFrame()
        layout.addWidget(widget)

        widget = StatInfoFrame()
        layout.addWidget(widget)

        widget = AppInfoFrame()
        layout.addWidget(widget)

    # --------        slots        --------
    def _onRefreshAction(self):

        # update visible
        visible = get_setting(key='widgetWindow/visible')
        self.setVisible(visible)

        # update widgets
        for object_name in ['lastRecordFrame', 'statInfoFrame']:
            widget = self.findChild(QtWidgets.QFrame, object_name)
            widget._onRefreshAction()


class WidgetWindow(BaseWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, objectName='widgetWindow', **kwargs)

        self.setWindowFlag(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        # icon
        filepath = pave(os.path.join('.', 'static', 'icon.ico'))
        icon = QtGui.QIcon(filepath)
        self.setWindowIcon(icon)

        # styles
        style = open(pave(os.path.join('.', 'static', 'widget.css')), 'r').read()
        self.setStyleSheet(style)

        # layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.widget = WidgetWidget()
        layout.addWidget(self.widget)

        # actions
        self._setdefault_actions()

    # --------        slots        --------
    def _onRefreshAction(self):

        # visible
        visible = get_setting(key='widgetWindow/visible')
        self.setVisible(visible)

        # styles
        style = open(pave(os.path.join('.', 'static', 'widget.css')), 'r').read()
        self.setStyleSheet(style)

        #
        self.widget._onRefreshAction()

    # --------        events        --------
    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        window = find_window('mainWindow')
        window.showNormal()

        event.accept()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self._beginPos = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        delta = QtCore.QPoint(event.globalPos() - self._beginPos)
        self.move(
            self.x() + delta.x(),
            self.y() + delta.y(),
        )

        self._beginPos = event.globalPos()

    def closeEvent(self, event: QtCore.QEvent):

        # update setting
        set_setting(
            key='widgetWindow/visible',
            value=False,
        )
        set_setting(
            key=f'geometry/{self.objectName()}',
            value=self.geometry(),
        )

        #
        event.accept()
