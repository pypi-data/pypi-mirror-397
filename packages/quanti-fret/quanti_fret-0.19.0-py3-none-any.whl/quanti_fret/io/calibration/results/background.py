from quanti_fret.io.base.results import StageResults
from quanti_fret.io.base.validate import (
    BackgroundEngineValidator, BackgroundResultsValidator, IntValidator,
    StringValidator, TupleValidator, Validator
)

from pathlib import Path


class BackgroundResults(StageResults):
    """ Manage the saving of the settings and results of the background stage.

    Tuples descriptions:

    * **settings**:

      * series names (``list[str]``).
      * series used (:any:`QtfSeries`): transformed in size of the series
        (``int``).
      * engine used (:any:`BackgroundEngine`).
    * **results**:

      * background: one of:

        * Disabled (``None``).
        * bckg_dd, bckg_da, bckg_aa (``tuple[float, float, float]``).
    * **extra**: Empty.
    * **triplets results**: Empty.
    * **triplets extra**: Empty.
    """

    VALIDATORS: dict[str, dict[str, Validator]] = {
        'settings': {
            'series': TupleValidator(StringValidator()),
            'nb_seq': IntValidator(min=0),
            'background_engine': BackgroundEngineValidator(),
        },
        'results': {
            'background': BackgroundResultsValidator(),
        }
    }

    def __init__(self, output_dir: Path):
        """Constructor.

        Args:
            output_dir (Path): Path to the output directory.
        """
        super().__init__(output_dir, self.VALIDATORS)
