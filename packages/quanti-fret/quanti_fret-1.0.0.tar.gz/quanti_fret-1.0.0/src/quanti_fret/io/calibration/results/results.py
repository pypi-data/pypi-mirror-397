from quanti_fret.io.base import ResultsManager
from quanti_fret.io.calibration.results.background import BackgroundResults
from quanti_fret.io.calibration.results.gamma import GammaResults
from quanti_fret.io.calibration.results.xm import XMResults

from pathlib import Path


class CalibrationResultsManager(ResultsManager):
    """ ResultsManager implementation for the calibration phase.

    Available stages are:

    * ``background``.
    * ``bt``.
    * ``de``.
    * ``xm``.

    The StageResults can be accessed by their name using the square brackets.
    """
    def __init__(self, output_path: Path) -> None:
        """Constructor

        Args:
            output_path (Path): Path to the output directory.
        """
        self._check_output_dir(output_path)
        managers = {
            'background': BackgroundResults(output_path / 'Background'),
            'bt': GammaResults(output_path / 'BT', 'alpha_bt', 'std_bt'),
            'de': GammaResults(output_path / 'DE', 'delta_de', 'std_de'),
            'xm': XMResults(output_path / 'XM'),
        }
        super().__init__(managers)
