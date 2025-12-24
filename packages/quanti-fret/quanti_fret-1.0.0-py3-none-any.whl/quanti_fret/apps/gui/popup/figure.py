from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.figure import Figure
from qtpy.QtCore import Signal
from qtpy.QtGui import QCloseEvent
from qtpy.QtWidgets import QDialog, QVBoxLayout, QWidget


class FigureDialog(QDialog):
    """ Open a matplotlib figure in a QDialog.

    This allow the display of matplotlib figures without the usage of ``plt``,
    but instead with the usage of **Qt**.

    This was inspired by:

    https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html

    It provides the following signal:

    * ``closed``: Signal that the Dialog was closed. This is used to signal
      the :any:`PopUpManager` that the dialog was closed and it can stop
      keeping this :class:`FigureDialog` in memory.
    """
    closed = Signal(QDialog)

    def __init__(self, figure: Figure, *args, **kwargs) -> None:
        """ Constructor.

        Args:
            figure (Figure): Figure to display.
        """
        super().__init__(*args, **kwargs)
        self._main = QWidget()
        layout = QVBoxLayout(self._main)
        self.setLayout(layout)

        static_canvas = FigureCanvasQTAgg(figure)
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        layout.addWidget(NavigationToolbar2QT(static_canvas, self))
        layout.addWidget(static_canvas)

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        """ Override closeEvent to delete itself from the PopupManager.
        """
        self.closed.emit(self)
        return super().closeEvent(a0)
