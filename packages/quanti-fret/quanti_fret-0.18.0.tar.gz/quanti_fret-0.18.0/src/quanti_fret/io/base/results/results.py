from quanti_fret.core import QtfException
from quanti_fret.io.base.results.stage import StageResults

from pathlib import Path


class ResultsManager:
    """ Entry point to save and get the settings and the results of all the
    stages of a phase.

    This class instanciates and gives access to all the :any:`StageResults`
    associated with a given phase.

    The :any:`StageResults` can be accessed by their name using the square
    brackets.

    Example:

    .. code:: Python

        results_manager['my_stage'].save_stage(settings, results)
        settings = results_manager['my_stage'].get_stage_settings()
        results = results_manager['my_stage'].get_stage_results()
        # ...

    """
    def __init__(self, stages_managers: dict[str, StageResults]) -> None:
        """Constructor.

        Args:
            stages_managers (dict[str, StageResults]): Dictionary containing
                all the stages names available to store the results, with their
                :any:`StageResults` associated.
        """
        self._managers = stages_managers

    def set_clean_all_output(self, val: bool) -> None:
        """ Decide whether or not to clean the entire output folder of a stages
        when calling its :any:`StageResults.clean_output` method.

        If set to ``True``, all the output folder will be deleted. Otherwise,
        only the dump folder will be deleted.

        Args:
            val (bool): Value to set.
        """
        for manager in self._managers.values():
            manager.set_clean_all_output(val)

    def __getitem__(self,  stage: str) -> StageResults:
        """ Get the :any:`StageResults` associated with the given stage.

        Args:
            stage (str): Stage name.

        Raises:
            QtfException: If the stage is unknown.

        Returns:
            StageResults: The StageResults associated.
        """
        if stage not in self._managers:
            err = f'No StageManager exists for stage "{stage}"'
            raise QtfException(err)
        return self._managers[stage]

    def _check_output_dir(self, output_dir: Path) -> None:
        """ Check if the output dir is valid.

        Args:
            output_dir (Path): path to test.

        Raises:
            QtfException: If the output dir is invalid.
        """
        if not isinstance(output_dir, Path):
            err = 'Output path is not an instance of Path'
            raise QtfException(err)
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
        if not output_dir.is_dir():
            err = f'Output path {output_dir} exists and is not a directory'
            raise QtfException(err)
