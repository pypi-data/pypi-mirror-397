from quanti_fret.core import QtfException, TripletSequence
from quanti_fret.io import ResultsManager

from qtpy.QtCore import QUrl
from qtpy.QtGui import QDesktopServices

import numpy as np


class StandalonePopUpManager:
    """ PopUp manager for the Standalone Mode.

    Opening sequences and Fret results will open the file manager to the
    appropriate folder.
    """

    def openSequence(self, seq: TripletSequence) -> None:
        """ Open the given Triplet sequence.

        This will launch the OS's file manager at the sequence's location.

        Args:
            seq (TripletSequence): Sequence to open.
        """
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(seq.folder)))

    def openFretResult(self, id: int, resultManager: ResultsManager) -> None:
        """ Open the given Triplet results.

        This will launch the OS's file manager at the results's location.

        Args:
            id (int): Id of the triplet to open.
            resultManager (ResultsManager): Result manager associated with the
                phase in order retrieve the elments to open.
        """
        path = resultManager['fret'].get_triplet_results_path(id)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def openArray(self, array: np.ndarray) -> None:
        """ Open a multidimentional array.

        This is not implemented in this mode, witll raise a
        :any:`QtfException`.

        Args:
            array_list (Figure): 3D Array to open.
        """
        err = '`openArray` is not implemented for StandalonePopUpManager'
        raise QtfException(err)
