from PySide6 import QtWidgets

from aims.settings import get_setting
from aims.widget.sheetWidget import SheetWidget


def _format_tab_label(label: str) -> str:
    """Format label to represent not empty tab's label."""
    return f'{label:<15}'


class QueueWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.tabWidget = QtWidgets.QTabWidget()
        for _ in range(self.n_sheets):
            widget = SheetWidget(
                parent=self,
            )
            self.tabWidget.addTab(widget, '')
        self.tabWidget.setCurrentIndex(0)
        layout.addWidget(self.tabWidget)

    @property
    def n_sheets(self) -> int:
        return get_setting(key='config/tracked_queue_length')

    # --------        slots        --------
    def _onRefreshTriggered(self):
        app = QtWidgets.QApplication.instance()

        for i in range(self.n_sheets):

            # get sheet
            try:
                datum = app.data[i]
            except IndexError:
                datum = None

            # update widget
            if datum is None:
                self.tabWidget.setTabVisible(i, False)
                self.tabWidget.setTabEnabled(i, False)
                self.tabWidget.setTabText(i, _format_tab_label(label=''))

            else:
                self.tabWidget.setTabVisible(i, True)
                self.tabWidget.setTabEnabled(i, True)
                self.tabWidget.setTabText(i, _format_tab_label(label=getattr(datum, 'probe_name', '')))

                widget = self.tabWidget.widget(i)
                widget._onRefreshTriggered(datum=datum)
