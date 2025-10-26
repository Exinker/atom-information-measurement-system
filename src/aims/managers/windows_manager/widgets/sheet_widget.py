import os

import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets

from aims.configs import COLOR
from aims.managers.data_manager import DataManager
from aims.managers.data_manager.data.data import DatumABC
from aims.managers.data_manager.utils.runners import run_explorer
from aims.settings import get_setting
from spectrumapp.numbers import format_number


N_ROWS_MAX = 10


class SheetWidget(QtWidgets.QWidget):

    def __init__(self, *args, data_manager: DataManager, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_manager = data_manager

        # layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.tableViews = []
        for _ in range(N_ROWS_MAX):
            view = TableView(
                parent=self,
            )
            layout.addWidget(view)

            self.tableViews.append(view)

    # --------        slots        --------
    def on_refreshed(self, datum: DatumABC | None = None):

        datum = datum or self.data_manager.last_datum
        if datum is None:
            return

        # process sheet
        datum = datum.filtrate(
            level=get_setting(key='table/filter-level'),
        )
        datum = datum.sort(
            kind=get_setting(key='table/sorter-kind'),
        )

        # update table views
        n_targets = 0  # len(datum.targets.columns)  # FIXME
        n_rows = min(
            get_setting(key='table/n_rows'),
            N_ROWS_MAX,
        )
        n_columns = max(
            get_setting(key='table/n_columns'),
            int(np.ceil(n_targets / n_rows)),
        )

        for i in range(N_ROWS_MAX):
            columns = datum.levels.index[slice(n_columns*(i), n_columns*(i + 1))]

            model = TableModel(
                datum=datum.select(columns=columns),
            )

            view = self.tableViews[i]
            view.setVisible(i < n_rows)
            # view.setVisible((i < n_rows) and (len(columns) > 0))
            view._update(
                model=model,
            )


class TableModel(QtCore.QAbstractTableModel):

    def __init__(
        self,
        *args,
        datum: DatumABC,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._data = datum.sheet

        self._n_meta_rows = len(set(datum.sheet.index) - set(datum.TARGET_ROW_NAMES))
        self._meta_columns = datum.META_COLUMN_NAMES
        self._meta_columns_visible = datum.META_COLUMN_NAMES_VISIBLE
        self._target_rows = datum.TARGET_ROW_NAMES
        self._target_columns = datum.levels.index.to_list()

    def data(self, index, role):
        row = self._data.index[index.row()]
        column = self._data.columns[index.column()]
        value = self._data.iloc[index.row()][column]

        try:
            if role == QtCore.Qt.DisplayRole:

                if column in ['probe_name', 'parallel_name']:
                    if row in self._target_rows:
                        return ''

                    return value

                if column in ['datetime']:
                    if True:
                        return value.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        return value.strftime('%H:%M:%S')

                if column in ['analysis_name', 'file_name']:
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
                    return QtGui.QColor('#E3E3E3') if self._n_meta_rows % 2 else QtGui.QColor('#F9F9F9')

                else:
                    if column in ['probe_name', 'parallel_name']:
                        is_certified = self._data['is_certified'].iloc[index.row()]

                        color = COLOR['green'] if is_certified else COLOR['yellow']
                        color = QtGui.QColor(color)
                        color.setAlphaF(.2)

                        return color

                    return QtGui.QColor('#E3E3E3') if index.row() % 2 else QtGui.QColor('#F9F9F9')

            elif role == QtCore.Qt.TextAlignmentRole:
                if column in ['datetime']:
                    return QtCore.Qt.AlignRight

                return QtCore.Qt.AlignLeft

        except ValueError:
            value = self._data.iloc[index.row()][column]
            return value

    def headerData(self, section, orientation, role):  # noqa: N802

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                column = self._data.columns[section]
                return column.replace('_', ' ')

            if orientation == QtCore.Qt.Vertical:
                row = self._data.index[section]
                if row in self._target_rows:
                    return row
                else:
                    value = self._data['datetime'].iloc[section]
                    return value.strftime('%Y-%m-%d %H:%M:%S')

    def rowCount(self, index):  # noqa: N802
        return self._data.shape[0]

    def columnCount(self, index):  # noqa: N802
        return self._data.shape[1]


class VerticalHeader(QtWidgets.QHeaderView):

    def __init__(
        self,
        *args,
        orientation=QtCore.Qt.Orientation.Vertical,
        **kwargs,
    ):
        super().__init__(*args, orientation, **kwargs)

        self.setDefaultSectionSize(25)
        self.setFixedWidth(140)
        self.sectionDoubleClicked.connect(self._on_dbl_clicked)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:  # noqa: N802

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            return super().mouseDoubleClickEvent(event)

    def _on_dbl_clicked(self, section: int):
        model = self.parent().model()
        data = model._data

        file_dir, file_name = data.iloc[section][['file_dir', 'file_name']]

        path = os.path.join(file_dir, file_name)
        run_explorer(path)


class TableView(QtWidgets.QTableView):

    def __init__(
        self,
        *args,
        model: QtCore.QAbstractTableModel | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if model is None:
            model = TableModel(
                datum=DatumABC.from_default(),
            )

        # model
        self.setModel(model)

        # selectionModel
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        # span
        self.clearSpans()

        # headers
        hh = self.horizontalHeader()
        hh.setFixedHeight(25)
        hh.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        vh = VerticalHeader(parent=self)
        self.setVerticalHeader(vh)

        # geometry
        # self.setMinimumSize(QtCore.QSize(5 + 120 + 15, 90))

    def _update(self, model: QtCore.QAbstractTableModel):

        # update style
        style = 'font-size: {font_size}px; font-weight: {font_weight}'.format(
            font_size=get_setting(key='style/font-size'),
            font_weight=get_setting(key='style/font-weight'),
        )
        self.setStyleSheet(style)

        # update model
        self.setModel(model)

        # update view
        n_target_columns = len(model._target_columns)
        for i, column in enumerate(model._meta_columns):
            is_hidden = not (column in model._meta_columns_visible)
            self.setColumnHidden(i, is_hidden)

        for i in range(len(model._meta_columns_visible) + n_target_columns):  # minus number of hidded columns
            self.setColumnWidth(i, 120)

        self.clearSpans()
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.scrollToBottom()

        # emit
        model.layoutChanged.emit()
