from PySide6 import QtCore, QtWidgets

from aims.settings import get_setting


class LastRecordFrame(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, objectName='lastRecordFrame', **kwargs)

        #
        layout = QtWidgets.QFormLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(0)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('organizationLabel')
        layout.addRow('Организация:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('deviceLabel')
        layout.addRow('Прибор:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        layout.addRow('', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('userLabel')
        layout.addRow('Оператор:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('analysisNameLabel')
        layout.addRow('Анализ:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        layout.addRow('', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('probeNameLabel')
        layout.addRow('Образц:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('probeDateLabel')
        layout.addRow('Дата:', widget)

        widget = QtWidgets.QLabel(text='', parent=self)
        widget.setObjectName('probeTimeLabel')
        layout.addRow('Время:', widget)

    # --------        slots        --------
    def _onRefreshTriggered(self):
        app = QtWidgets.QApplication.instance()

        datum = app.data.last_datum
        meta = datum.last_meta

        if meta is None:  # FIXME: remove it
            return

        widget = self.findChild(QtWidgets.QLabel, 'organizationLabel')
        widget.setText(
            f'<strong>{meta.organization_name}</strong>',
        )

        widget = self.findChild(QtWidgets.QLabel, 'deviceLabel')
        widget.setText(
            f'<strong>{meta.device_name}</strong>',
        )

        widget = self.findChild(QtWidgets.QLabel, 'userLabel')
        widget.setText(
            f'{meta.user_name}',
        )

        widget = self.findChild(QtWidgets.QLabel, 'probeNameLabel')
        widget.setText(
            f'{meta.name}',
        )

        widget = self.findChild(QtWidgets.QLabel, 'probeDateLabel')
        widget.setText(
            f'{meta.datetime.date()}',
        )

        widget = self.findChild(QtWidgets.QLabel, 'probeTimeLabel')
        widget.setText(
            f'{meta.datetime.time()}',
        )

        widget = self.findChild(QtWidgets.QLabel, 'analysisNameLabel')
        widget.setText(
            f'{meta.analysis_name}',
        )


class MetaWidget(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addSpacing(20)

        widget = LastRecordFrame()
        layout.addWidget(widget)

    # --------        slots        --------
    def _onRefreshTriggered(self):

        # update visible
        visible = get_setting(key='mainWindow/meta-widget')
        self.setVisible(visible)

        # update widgets
        for object_name in ['lastRecordFrame']:
            widget = self.findChild(QtWidgets.QFrame, object_name)
            widget._onRefreshTriggered()
