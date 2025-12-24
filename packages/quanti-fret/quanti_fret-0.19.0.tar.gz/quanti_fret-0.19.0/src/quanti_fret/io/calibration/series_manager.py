from quanti_fret.io.base.series_manager import QtfSeriesManager


class QtfCalibrationSeriesManager(QtfSeriesManager):
    """ SerieManager implementation for the calibration phase.

    Series accepted are:

    * ``donors``.
    * ``acceptors``.
    * ``standards``.
    """
    def __init__(self) -> None:
        """ Constructor
        """
        super().__init__(['donors', 'acceptors', 'standards'])
