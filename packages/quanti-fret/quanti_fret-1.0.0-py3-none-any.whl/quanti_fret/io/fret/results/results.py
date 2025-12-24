from quanti_fret.io.base import ResultsManager
from quanti_fret.io.fret.results.fret import FretResults, StageResults

from pathlib import Path


class FretResultsManager(ResultsManager):
    """ ResultsManager implementation for the FRET phase.

    Available stages are:

    * ``fret``.

    The StageResults can be accessed by their name using the square brackets.
    """

    def __init__(self, output_path: Path) -> None:
        """Constructor.

        Args:
            output_path (Path): Path to the output directory.
        """
        self._check_output_dir(output_path)
        managers: dict[str, StageResults] = {
            'fret': FretResults(output_path),
        }
        super().__init__(managers)
