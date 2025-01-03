from PySide6 import QtWidgets

from aims.managers.data_manager import DataManager
from aims.managers.windows_manager.widgets.sheetWidget import SheetWidget
from aims.settings import get_setting


def _format_tab_label(label: str) -> str:
    """Format label to represent not empty tab's label."""
    return f'{label:<15}'


class SheetQueueWidget(QtWidgets.QWidget):

    def __init__(self, *args, data_manager: DataManager, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_manager = data_manager

        # layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.tabWidget = QtWidgets.QTabWidget()
        for _ in range(self.n_sheets):
            widget = SheetWidget(
                data_manager=data_manager,
                parent=self,
            )
            self.tabWidget.addTab(widget, '')
        self.tabWidget.setCurrentIndex(0)
        layout.addWidget(self.tabWidget)

    @property
    def n_sheets(self) -> int:
        return get_setting(key='config/tracked_queue_length')

    # --------        slots        --------
    def _on_refresh_triggered(self):

        for i in range(self.n_sheets):

            # get sheet
            try:
                datum = self.data_manager.data[i]
            except (IndexError, TypeError):
                datum = None

            # update widget
            if datum is None:
                self.tabWidget.setTabVisible(i, False)
                self.tabWidget.setTabEnabled(i, False)
                self.tabWidget.setTabText(i, _format_tab_label(label=''))

            else:
                self.tabWidget.setTabVisible(i, True)
                self.tabWidget.setTabEnabled(i, True)
                self.tabWidget.setTabText(i, _format_tab_label(label=datum.meta.probe_name))

                widget = self.tabWidget.widget(i)
                widget._on_refresh_triggered(datum=datum)
