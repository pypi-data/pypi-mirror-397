from quanti_fret.io.base.series_manager import QtfSeriesManager


class QtfFretSeriesManager(QtfSeriesManager):
    """ SerieManager implementation for the FRET phase.

    Series accepted are:

    * ``experiments``.
    """

    def __init__(self) -> None:
        """ Constructor.
        """
        super().__init__(['experiments'])
