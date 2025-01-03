from PySide6 import QtCore, QtWidgets

from aims.managers.data_manager import DataManager
from aims.settings import get_setting


class LastRecordFrame(QtWidgets.QFrame):

    def __init__(self, *args, data_manager: DataManager, **kwargs):
        super().__init__(*args, objectName='lastRecordFrame', **kwargs)

        self.data_manager = data_manager

        #
        layout = QtWidgets.QFormLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(0)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('organizationNameLabel')
        layout.addRow('Организация:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('deviceNameLabel')
        layout.addRow('Прибор:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        layout.addRow('', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('userNameLabel')
        layout.addRow('Оператор:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('analysisNameLabel')
        layout.addRow('Анализ:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        layout.addRow('', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('probeNameLabel')
        layout.addRow('Образец:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('probeDateLabel')
        layout.addRow('Дата:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('probeTimeLabel')
        layout.addRow('Время:', widget)

    # --------        slots        --------
    def _on_refresh_triggered(self):
        pass

        # datum = self.data_manager.last_datum
        # meta = datum.meta

        # widget = self.findChild(QtWidgets.QLabel, 'organizationNameLabel')
        # widget.setText(
        #     f'<strong>{meta.organization_name}</strong>',
        # )

        # widget = self.findChild(QtWidgets.QLabel, 'deviceNameLabel')
        # widget.setText(
        #     f'<strong>{meta.device_name}</strong>',
        # )

        # widget = self.findChild(QtWidgets.QLabel, 'userNameLabel')
        # widget.setText(
        #     f'{meta.user_name}',
        # )

        # widget = self.findChild(QtWidgets.QLabel, 'analysisNameLabel')
        # widget.setText(
        #     f'{meta.analysis_name}',
        # )

        # widget = self.findChild(QtWidgets.QLabel, 'probeNameLabel')
        # widget.setText(
        #     f'{meta.probe_name}',
        # )

        # widget = self.findChild(QtWidgets.QLabel, 'probeDateLabel')
        # widget.setText(
        #     f'{meta.datetime.date()}',
        # )

        # widget = self.findChild(QtWidgets.QLabel, 'probeTimeLabel')
        # widget.setText(
        #     f'{meta.datetime.time()}',
        # )


class MetaWidget(QtWidgets.QFrame):

    def __init__(self, *args, data_manager: DataManager, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_manager = data_manager

        #
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addSpacing(20)

        widget = LastRecordFrame(
            data_manager=self.data_manager,
        )
        layout.addWidget(widget)

    # --------        slots        --------
    def _on_refresh_triggered(self):

        # update visible
        visible = get_setting(key='mainWindow/meta-widget')
        self.setVisible(visible)

        # update widgets
        for object_name in ['lastRecordFrame']:
            widget = self.findChild(QtWidgets.QFrame, object_name)
            widget._on_refresh_triggered()
