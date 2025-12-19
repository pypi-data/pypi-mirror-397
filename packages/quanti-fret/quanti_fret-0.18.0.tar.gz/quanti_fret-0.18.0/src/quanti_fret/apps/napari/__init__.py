
from quanti_fret.apps.gui import QtfMainWidget
from quanti_fret.apps.gui.popup import PopUpManager

from qtpy.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import napari   # type: ignore


class QtfNapariWidget(QWidget):
    """ Entry point widget for the Napari plugin.
    """
    def __init__(
        self, viewer: "napari.viewer.Viewer", parent: QWidget | None = None
    ) -> None:
        """ Constructor.

        This set the :any:`PopUpManager` to napari mode, and instanciate the
        :any:`QtfMainWidget`.

        Args:
            viewer (napari.viewer.Viewer): Napari viewer.
            parent (QWidget | None, optional): Parent widget. Defaults to
                ``None``.
        """
        super().__init__(parent=parent)

        PopUpManager().setNapariMode(viewer)

        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(QtfMainWidget(parent=self))
