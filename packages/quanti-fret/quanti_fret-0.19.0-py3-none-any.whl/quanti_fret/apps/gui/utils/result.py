from quanti_fret.algo import (
    BackgroundEngine, BackgroundEnginePercentile, BackgroundEngineFixed
)

from typing import Any

from qtpy.QtCore import QSize
from qtpy.QtGui import QPalette
from qtpy.QtWidgets import (
    QGridLayout,
    QLabel,
    QLineEdit,
    QWidget,
)


class ResultCells:
    """ Handle the display of a stage result.

    The result consist on two widgets:

    * A title label.
    * A non editable line edit containing the value of the result.

    Results usually don't come alone, so for fancy display, this class was
    designed to store results widgets inside a ``QGridLayout`` passed as
    parameter. It will add the title at the column and row passed to the
    constructor, then the result at the same row but next column.

    You can change the title and the results by calling:

    * :meth:`setTitle`.
    * :meth:`setResult` (will try to parse the result into a ``str``).

    In order to differenciate the results from stage, from the important ones
    from the ones used as settings, the following method were implemented:

    * :meth:`setBold`: Results and title font will be bold.
    * :meth:`setEnabled`: Set the enabled mode of both title and result widget.
    * :meth:`setLocked`: Set the ``locked`` mode. In ``locked`` mode, disable
      only the result widget.
    """
    def __init__(
        self, parent: QWidget,  title: str, grid: QGridLayout, row: int,
        col: int = 0,
    ):
        """ Constructor.

        Args:
            parent (QWidget): Parent widget.
            title (str): Title of the widget.
            grid (QGridLayout): Grid to put the widgets on.
            row (int): Row on the grid.
            col (int, optional): First column on the grid. Default is 0.
        """
        self._locked = False

        # Title
        self._titleLabel = QLabel(f'{title}:', parent=parent)
        grid.addWidget(self._titleLabel, row, col)

        # Result
        self._result = IgnoredSizeLineEdit(parent=parent)
        self._result.setReadOnly(True)
        # self._result.setSizePolicy(
        #     QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        # )
        grid.addWidget(self._result, row, col + 1)

        # Change Result background color
        palette = self._result.palette()
        color = palette.color(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base
        )
        palette.setColor(self._result.backgroundRole(), color)
        self._result.setPalette(palette)

    def setResult(self, result: Any | None) -> None:
        """ Update the display to the given result.

        Args:
            result (Any | None): Result to set. If not, will print a no result
                display.
        """
        if result is None:
            self._result.setText('-')
        else:
            self._result.setText(str(result))

    def setTitle(self, title: str) -> None:
        """ Change the title of the widget.

        Args:
            title (str): New title to set.
        """
        self._titleLabel.setText(title)

    def setBold(self, bold: bool) -> None:
        """ Set or unset the text being bold.

        Args:
            bold (bool): True to set the bold value.
        """
        # Title
        font = self._titleLabel.font()
        font.setBold(bold)
        self._titleLabel.setFont(font)

        # result
        font = self._result.font()
        font.setBold(bold)
        self._result.setFont(font)

    def setEnabled(self, enabled: bool) -> None:
        """ Enable or not the widgets.

        Args:
            enabled (bool): True to enable.
        """
        self._titleLabel.setEnabled(enabled)
        if self._locked:
            self._result.setEnabled(False)
        else:
            self._result.setEnabled(enabled)

    def setLocked(self, locked: bool) -> None:
        """ Set the widget in settings locked mode.

        Args:
            enabled (bool): True to set.
        """
        self._locked = locked
        self._result.setEnabled(not locked)

    def show(self) -> None:
        """ Show both the title and the result.
        """
        self._titleLabel.show()
        self._result.show()

    def hide(self) -> None:
        """ Hide both the title and the result.
        """
        self._titleLabel.hide()
        self._result.hide()


class BackgroundResultCells(ResultCells):
    """ ResultsCell for a background engine.

    When setting a background engine results, it will display:

    * The mode of the engine
    * In parenthesis:

      * The fixed values for fixed mode.
      * The percentile value for percentile mode.
    """
    def __init__(
        self, parent: QWidget,  title: str, grid: QGridLayout, row: int,
        col: int = 0,
    ):
        """ Constructor.

        Args:
            parent (QWidget): Parent widget.
            title (str): Title of the widget.
            grid (QGridLayout): Grid to put the widgets on.
            row (int): Row on the grid.
            col (int, optional): First column on the grid. Default is 0.
        """
        super().__init__(parent, title, grid, row, col)

    def setResult(self, result: Any | None) -> None:
        """ Update the display to the given result

        Args:
            result (Any | None): Result to set. If not, will print a no result
                display
        """
        if result is None:
            self._result.setText('-')
        else:
            assert isinstance(result, BackgroundEngine)
            text = f'{result.mode}'
            if isinstance(result, BackgroundEnginePercentile):
                text += f' ({result._percentile})'
            elif isinstance(result, BackgroundEngineFixed):
                text += f' {result.background}'
            self._result.setText(text)


class IgnoredSizeLineEdit(QLineEdit):
    """ Custom ``QLineEdit`` that prevents **Qt** to use this widget default
    width in order to estimate the windows width.

    I need it for nicer display!
    """
    def sizeHint(self):
        return QSize(0, super().sizeHint().height())

    def minimumSizeHint(self):
        return QSize(0, super().minimumSizeHint().height())
