from quanti_fret.io.fret.config import FretConfig
from quanti_fret.io.calibration import CalibrationResultsManager

from quanti_fret.algo import BackgroundEngine
from quanti_fret.core import QtfSeries, QtfException
from quanti_fret.io.base import (
    Config,
    ResultsManager,
    QtfSeriesManager,
    StageParams,
)

from typing import Any


class FretStageParams(StageParams):
    """ StageParams implementation for the FRET phase.

    Accepted stages are:

    * ``fret``: Fret params for the stage run.
    * ``fret_params``: Fret params without the series associated.
    * ``cali_background``: Background value from calibration.
    """

    def __init__(
        self, config: Config, series_manager: QtfSeriesManager,
        results_manager: ResultsManager | None
    ) -> None:
        """ Constructor.

        Args:
            config (Config): Config to use.
            series_manager (QtfSeriesManager): Series Manager to use.
            results_manager (ResultsManager): Results Manager to use.
        """
        if type(config) is not FretConfig:
            raise QtfException('Unexpected Config type')
        if results_manager is not None and \
           type(results_manager) is not CalibrationResultsManager:
            raise QtfException('Unexpected ResultsManager type')

        self._config = config
        self._series = series_manager
        self._results = results_manager
        super().__init__()

    def get(
        self, stage: str, allow_none_values: bool = False
    ) -> tuple[Any, ...]:
        """ Get the parameters of the stage passed in arguments.

        Args:
            stage (str): Stage to get the parameters for. Must be in
                ``['fret', 'fret_params', 'cali_background']``.
            allow_none_values (bool, optional): If ``true``, will not raise
                exceptions if elements are missing for the run, instead values
                not found will be set to ``None``. Defaults to ``False``.

        Raises:
            QtfException: The stage is unknown.
            QtfException: Parameters are missing and ``allow_none_values`` is
                set to ``False``.

        Returns:
            tuple[Any, ...]:
                The parameters to run the stage (see each stage's method
                implementation for more information).
        """
        stages_gets = {
            'fret': self.fret,
            'fret_params': self.fret_params,
            'cali_background': self.cali_background,
        }
        if stage not in stages_gets:
            raise QtfException(f'Unknown stage {stage}')
        return stages_gets[stage](allow_none_values)

    def fret(
        self, allow_none_values: bool = False
    ) -> tuple[str, QtfSeries, float | None, float | None, float | None,
               float | None, BackgroundEngine | None, float, float, float,
               float, bool, int]:
        """  Get the params for the Fret to run on a full series.

        Args:
            allow_none_values (bool, optional): If ``true``, will not raise
                exceptions if elements are missing for the run, instead values
                not found will be set to ``None``. Defaults to ``False``.

        Raises:
            QtfException: Parameters are missing and ``allow_none_values`` is
                set to ``False``.

        Returns:
            tuple[str, QtfSeries, float | None, float | None, float | None, \
                  float | None, BackgroundEngine | None, float, float, float, \
                  float, bool, int]:
            * Name of the series.
            * Series to use.
            * Alpha BT value.
            * Delta DE value.
            * BetaX value.
            * GammaM DE value.
            * Background engine.
            * Target S value.
            * Sigma S value.
            * Sigma Gauss value.
            * Weights Threshold value.
            * Save analysis details.
            * Sampling.
        """
        # Get series
        series = self._series.get('experiments')
        if series.size == 0 and not allow_none_values:
            raise QtfException('0 Sequences found')

        params = self.fret_params(allow_none_values)
        background = params[4]
        self._validate_series_for_background(background, series,
                                             allow_none_values)

        return ('experiments', series, *params)

    def fret_params(
        self, allow_none_values: bool = False
    ) -> tuple[float | None, float | None, float | None, float | None,
               BackgroundEngine | None, float, float, float, float, bool, int]:
        """  Get the params for the Fret set_params method.

        These are the Fret params without the series associated. Use this to
        run on single triplet.

        Args:
            allow_none_values (bool, optional): If ``true``, will not raise
                exceptions if elements are missing for the run, instead values
                not found will be set to ``None``. Defaults to ``False``.

        Raises:
            QtfException: Parameters are missing and ``allow_none_values`` is
                set to ``False``.

        Returns:
            tuple[float | None, float | None, float | None, float | None, \
                  BackgroundEngine | None, float, float, float, float, bool, \
                  int]:
            * Alpha BT value.
            * Delta DE value.
            * BetaX value.
            * GammaM DE value.
            * Background engine.
            * Target S value.
            * Sigma S value.
            * Sigma Gauss value.
            * Weights Threshold value.
            * Save analysis details.
            * Sampling.
        """
        # Get Fret settings from config
        target_s: float = self._config.get('Fret', 'target_s')
        sigma_s: float = self._config.get('Fret', 'sigma_s')
        sigma_gauss: float = self._config.get('Fret', 'sigma_gauss')
        weights_threshold: float = self._config.get('Fret',
                                                    'weights_threshold')
        analysis_details: bool = self._config.get('Fret',
                                                  'save_analysis_details')
        analysis_sampling: int = self._config.get('Fret',
                                                  'analysis_sampling')

        # Get Background settings
        background = self._get_background_engine_from_config(self._config)

        if self._results is None:
            if not allow_none_values:
                raise QtfException('No Calibration config file set')
            else:
                alpha_bt = None
                delta_de = None
                beta_x = None
                gamma_m = None
        else:
            # Retrieve calibration results
            if background is None:
                res = self._results['background'].get_stage_results()
                if res is None:
                    if not allow_none_values:
                        raise QtfException('No Background results found')
                    background = None
                else:
                    background, = res

            res = self._results['bt'].get_stage_results()
            if res is None:
                if not allow_none_values:
                    raise QtfException('No BT results found')
                alpha_bt = None
            else:
                alpha_bt, _, _ = res

            res = self._results['de'].get_stage_results()
            if res is None:
                if not allow_none_values:
                    raise QtfException('No DE results found')
                delta_de = None
            else:
                delta_de, _, _ = res

            res = self._results['xm'].get_stage_results()
            if res is None:
                if not allow_none_values:
                    raise QtfException('No XM results found')
                beta_x = None
                gamma_m = None
            else:
                beta_x, gamma_m, _, _, _ = res

        return (
            alpha_bt, delta_de, beta_x, gamma_m, background,
            target_s, sigma_s, sigma_gauss, weights_threshold,
            analysis_details, analysis_sampling,
        )

    def cali_background(
        self, allow_none_values: bool = False
    ) -> tuple[BackgroundEngine | None]:
        """  Get the background value from calibration.

        Args:
            allow_none_values (bool, optional): If ``true``, will not raise
                exceptions if elements are missing for the run, instead values
                not found will be set to ``None``. Defaults to ``False``.

        Raises:
            QtfException: Parameters are missing and ``allow_none_values`` is
                set to ``False``.

        Returns:
            tuple[BackgroundEngine | None]:
                Background engine from calibration or ``None`` if no results is
                found.
        """
        if self._results is None:
            if not allow_none_values:
                raise QtfException('No Calibration config file set')
            else:
                background = None
        else:
            # Retrieve calibration results
            res = self._results['background'].get_stage_results()
            if res is None:
                if not allow_none_values:
                    raise QtfException('No Background results found')
                background = None
            else:
                background, = res

        return (background,)
