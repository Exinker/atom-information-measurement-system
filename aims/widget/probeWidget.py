import os

import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets

from spectrumapp.colors import COLOR
from spectrumapp.numbers import format_number

from aims.core.sheets import Sheet
from aims.core.utils import run_explorer
from aims.settings import get_setting


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, *args, sheet: Sheet, **kwargs):
        super().__init__(*args, **kwargs)

        #
        _data = sheet.to_frame()
        # if 'datetime' in _data:
        #     _data = _data.sort_values(by='datetime', axis=0)

        self._data = _data

        self._n_probes = len(sheet.prediction.index)
        self._n_target_columns = len(sheet.targets.columns)
        self._target_rows = sheet.targets.index.to_list()
        self._target_columns = sheet.targets.columns

    def data(self, index, role):
        row = self._data.index[index.row()]
        column = self._data.columns[index.column()]
        value = self._data.iloc[index.row()][column]

        try:
            if role == QtCore.Qt.DisplayRole:

                if column in ('probe_name', ):
                    if row in self._target_rows:
                        return ''

                    return value

                if column in ('datetime', ):
                    if True:
                        return value.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        return value.strftime('%H:%M:%S')

                if column in ('analysis_name', 'file_name'):
                    if row in self._target_rows:
                        return ''
                    else:
                        return value

                if column in self._target_columns:

                    if row in self._target_rows:
                        return format_number(value)

                    else:
                        if isinstance(value, str):
                            if value == 'nan':
                                return ''

                            return value

                        if np.isfinite(value):
                            return f'{value}'

                        else:
                            return ''

            if role == QtCore.Qt.FontRole:
                if row in self._target_rows:
                    if (row == 'ОСКО, %') and (column in self._target_columns):
                        value = self._data.loc[row, column]

                        if value >= 5:  # FIXME:
                            font = QtGui.QFont()
                            font.setBold(True)

                            return font

            if role == QtCore.Qt.ForegroundRole:
                if row in self._target_rows:
                    if (row == 'ОСКО, %') and (column in self._target_columns):
                        value = self._data.loc[row, column]

                        if value >= 10:  # FIXME:
                            return QtGui.QColor(COLOR['red'])
                        if value >= 5:  # FIXME:
                            return QtGui.QColor(COLOR['orange'])

            if role == QtCore.Qt.BackgroundRole:
                if row in self._target_rows:
                    return QtGui.QColor('#E3E3E3') if self._n_probes % 2 else QtGui.QColor('#F9F9F9')

                else:
                    if column in ('probe_name', ):
                        is_certified = self._data.loc[index.row(), 'is_certified']

                        color = COLOR['green'] if is_certified else COLOR['yellow']
                        color = QtGui.QColor(color)
                        color.setAlphaF(.2)

                        return color

                    return QtGui.QColor('#E3E3E3') if row % 2 else QtGui.QColor('#F9F9F9')

            elif role == QtCore.Qt.TextAlignmentRole:
                if column in ('datetime', ):
                    return QtCore.Qt.AlignRight

                return QtCore.Qt.AlignLeft

        except ValueError:
            value = self._data.iloc[index.row()][column]
            return value

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                column = self._data.columns[section]
                return column.replace('_', ' ')

            if orientation == QtCore.Qt.Vertical:
                row = self._data.index[section]
                if row in self._target_rows:
                    return row
                else:
                    value = self._data['datetime'].loc[section]
                    return value.strftime('%Y-%m-%d %H:%M:%S')

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]


class VerticalHeader(QtWidgets.QHeaderView):

    def __init__(self, *args, orientation=QtCore.Qt.Orientation.Vertical, **kwargs):
        super().__init__(*args, orientation, **kwargs)

        self.setDefaultSectionSize(25)
        self.setFixedWidth(140)
        self.sectionDoubleClicked.connect(self._on_dbl_clicked)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            return super().mouseDoubleClickEvent(event)

    def _on_dbl_clicked(self, section: int):
        model = self.parent().model()
        data = model._data

        file_dir, file_name = data.iloc[section][['file_dir', 'file_name']]

        path = os.path.join(file_dir, file_name)
        run_explorer(path)


class TableView(QtWidgets.QTableView):

    def __init__(self, *args, model: QtCore.QAbstractTableModel | None = None, **kwargs):
        super().__init__(*args, **kwargs)

        if model is None:
            model = TableModel(
                sheet=Sheet.from_default(),
            )

        data = model._data
        n_target_columns = model._n_target_columns
        n_info_columns = len(data.columns) - n_target_columns

        # style
        self.setStyleSheet("font-size: 14px; font-weight: 500")

        # viewModel
        self.setModel(model)

        # selectionModel
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        # span
        self.clearSpans()

        # headers
        hidden_columns = [0, 1, 2, 3, 4, 5, 6, 8]
        for column in hidden_columns:
            self.setColumnHidden(column, True)

        for i in range(n_info_columns - len(hidden_columns)):  # minus number of hidded columns
            self.setColumnWidth(i, 120)

        for i in range(n_target_columns):
            self.setColumnWidth(n_info_columns + i, 90)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        hh = self.horizontalHeader()
        hh.setFixedHeight(25)
        hh.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        vh = VerticalHeader(parent=self)
        self.setVerticalHeader(vh)

        # vh.hide()

        # geometry
        self.setMinimumSize(QtCore.QSize(5 + 120 + 15, 240))

    def _update(self, model: QtCore.QAbstractTableModel):

        # update viewModel
        self.setModel(model)

        # update selectionModel
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        # span
        self.clearSpans()


class ProbeWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.tableView = TableView(
            parent=self,
        )
        layout.addWidget(self.tableView)

    # --------        slots        --------
    def _onRefreshTriggered(self, sheet: Sheet | None = None):
        app = QtWidgets.QApplication.instance()

        # get sheet
        sheet = sheet or app.sheets.last_sheet

        if sheet is None:
            return

        # process sheet
        sheet = sheet.filtrate(
            level=get_setting(key='filter/level'),
        )
        sheet = sheet.sort(
            kind=get_setting(key='sorter/kind'),
        )

        # update table view
        model = TableModel(sheet=sheet)

        self.tableView._update(
            model=model,
        )
        model.layoutChanged.emit()
