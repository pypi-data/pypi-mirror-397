from quanti_fret.apps.gui.popup.figure import FigureDialog
from quanti_fret.apps.gui.popup.napari import NapariPopUpManager
from quanti_fret.apps.gui.popup.standalone import StandalonePopUpManager
from quanti_fret.io import ResultsManager

from quanti_fret.core import Singleton, TripletSequence

from typing import Any

from matplotlib.figure import Figure
import numpy as np


class PopUpManager(metaclass=Singleton):
    """ Manage actions that open **QuanTI-FRET** elements outside of the main
    GUI.

    There are two modes of the manager:

    * **Standalone** mode (default): *QuanTI-FRET* is being used as a
      standalone application. So all elements opened outside must open new
      windows.
    * **Napari** mode: *QuanTI-FRET* is being used insde *Napari* as a
      plugin. Arrays to open are opened inside *Napari*.

    This manager is a singleton, which means that if you need to set the Napari
    mode, you have to do it only once.

    This does not handle the files/folders Dialogs popup.

    This class keeps in memory all the dialog opened otherwise they would not
    remain opened. To close all dialogs opened when closing the app, call
    :meth:`PopUpManager.closeAll()` at the en of your program.

    """

    def __init__(self) -> None:
        """ Constructor.
        """
        self._viewer: StandalonePopUpManager | NapariPopUpManager
        self._viewer = StandalonePopUpManager()
        self._dialogs: list[FigureDialog] = []

    def setNapariMode(self, viewer: Any) -> None:
        """ Set the Mode to **Napari**.

        All arrays will be opened inside *Napari*.

        Args:
            viewer (napari.viewer.Viewer): Napari Viewer associated with the
                plugin. Used to open arrays.
        """
        self._viewer = NapariPopUpManager(viewer)

    def hasNapariMode(self) -> bool:
        """ Check if the popupmanager is in **Napari** mode or not.

        This is usefull to show buttons available only in *Napari*.

        Returns:
            bool: ``True`` if in napari mode.
        """
        return type(self._viewer) is NapariPopUpManager

    def openSequence(self, seq: TripletSequence) -> None:
        """ Open the given Triplet sequence.

        In **Napari** mode, will open the sequence inside *Napari*.

        Args:
            seq (TripletSequence): Sequence to open.
        """
        self._viewer.openSequence(seq)

    def openFretResult(self, id: int, resultManager: ResultsManager) -> None:
        """ Open the given FRET results.

        In **Napari** mode, will open the results inside *Napari*.

        Args:
            id (int): Id of the triplet to open.
            resultManager (ResultsManager): Result manager associated with the
                phase in order retrieve the elments to open.
        """
        self._viewer.openFretResult(id, resultManager)

    def openFigure(self, figure: Figure, title: str = '') -> None:
        """ Open a Figure into a QDialog.

        Args:
            figure (Figure): Figure to open.
            title (str, optional): Title to set. Default is ''.
        """
        dialog = FigureDialog(figure)
        if title != '':
            dialog.setWindowTitle(title)
        dialog.show()
        dialog.closed.connect(self._deleteDialog)
        self._dialogs.append(dialog)

    def openArray(self, array: np.ndarray) -> None:
        """ Open a 3D array plane in *Napari*.

        .. warning::

            Implemented only in **Napari** mode.

        Args:
            array (np.ndarray): 3D Array to open.
        """
        self._viewer.openArray(array)

    def closeAll(self) -> None:
        """Close all opened windows.
        """
        self._dialogs.clear()

    def _deleteDialog(self, dialog: FigureDialog) -> None:
        """ Delete the given :any:`FigureDialog` from the list.

        This is linked to the :any:`FigureDialog.closed` signal.

        Args:
            dialog (FigureDialog): Dialog to delete.
        """
        self._dialogs.remove(dialog)
