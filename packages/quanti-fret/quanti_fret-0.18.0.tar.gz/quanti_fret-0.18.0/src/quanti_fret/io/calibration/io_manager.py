
from quanti_fret.io.base import IOPhaseManager
from quanti_fret.io.calibration.config import CalibrationConfig
from quanti_fret.io.calibration.results import CalibrationResultsManager
from quanti_fret.io.calibration.stage_params import CalibrationStageParams
from quanti_fret.io.calibration.series_manager import (
    QtfCalibrationSeriesManager
)

from pathlib import Path


class CalibrationIOPhaseManager(IOPhaseManager):
    """ IOPhaseManager implementation for the calibration phase.
    """

    def __init__(self, load_series: bool = True) -> None:
        """ Constructor.

        Args:
            load_series (bool, optional): If ``True``, the IOPhaseManager will
                load the series itself using the values found in config.
                Otherwise, it is let to the user to handle the series loading.
                Defaults to ``True``.
        """
        super().__init__('calibration', load_series, exclude_disabled_seq=True)

    def _updated_config(self, section: str, key: str) -> None:
        super()._updated_config(section, key)
        if self._allow_updates:
            if section == 'Output' and key == 'output_dir':
                self._new_stage_params()
                if self._iopm_to_notify is not None:
                    val = self.config.get(section, key)
                    self._iopm_to_notify.external_config_update(
                        section, key, val)

    def _create_config(self, config_path: Path) -> None:
        # Config
        self._config = CalibrationConfig()

    def _create_series_manager(self, load_series: bool) -> None:
        assert self._config is not None
        self._series_manager = QtfCalibrationSeriesManager()
        if load_series:
            for series in ['donors', 'acceptors', 'standards']:
                self._reset_series(series)

    def _create_results_manager(self) -> None:
        assert self._config is not None
        output_path: Path = self.config.get('Output', 'output_dir')
        self._results_manager = CalibrationResultsManager(output_path)

    def _create_stage_params(self) -> None:
        assert self._config is not None
        assert self._series_manager is not None
        assert self._results_manager is not None
        self._stage_params = CalibrationStageParams(
            self._config, self._series_manager, self._results_manager)
