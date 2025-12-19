from quanti_fret.apps.gui.runner import CalculatorRunner
from quanti_fret.apps.gui.io_gui_manager import IOPhaseGuiManager
from quanti_fret.apps.gui.utils import (
    CollapsibleBox, LoadingAnimationLayout, LoadingProgressLayout
)

from quanti_fret.core import QtfException

import abc
from typing import Any

from qtpy.QtCore import Qt, QObject, QUrl
from qtpy.QtGui import QDesktopServices, QPalette
from qtpy.QtWidgets import (
    QFrame,
    QGroupBox,
    QLayout,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class QABCMeta(abc.ABCMeta, type(QObject)):  # type: ignore
    """ Metaclass to allow a QObject to have an abc.ABCMeta metaclass
    """
    pass


class StageCalculatorWidget(QScrollArea, metaclass=QABCMeta):
    """ Generic class to handle a stage that perform a computation.

    This is designed to we inherited for every specific stages.

    This widget is composed of 3 different sections:

    * One Box for the settings.
    * One Button to trigger the run.
    * One Box that displays the results.

    Settings box:
        Must be filled by the subclass by implementing the method
        :meth:`_buildSettings`.

        It is let to the subclass to update the config when a settings widget
        value is modified.

        Settings are expected to be updated when the IOPGM associated with the
        phase emits it's signal :any:`IOPhaseGuiManager.stateChanged`. In this
        case, this widget will do the following:

        .. code:: Python

            self._blockAllSignals(True)
            self._updateSettings()
            self._blockAllSignals(False)

        It is let to the subclass to implement the method
        :meth:`_blockAllSignals`. It's purpose is to block or unblock the
        signals emitted by the settings widget. If the settings widget signals
        are not blocked during update from the config, they might call the
        :any:`Config.set` method with their new value, which will emit more
        signals than needed.

        It is let to the subclass to implement the method
        :meth:`_updateSettings` that updates the settings widgets with the
        contents of the config or previous results. This method is also called
        right after the initialization to fill the settings with config values.

    Run Button:
        This is the button that run's the associated stage using the
        :any:`CalculatorRunner.run` method.

        It uses the params returned by the :any:`StageParams.get` method in
        order to:

        * Inform the user if params are missing for the run (in this case, the
          button will not be activated).
        * Inform the user of the number of triplet that will be used for the
          run.
        * Execute the run when pressed.

        If another stage is already running, the run button will be disabled.

        During the run of the stage, the button can also display the progress
        of the run if available.

    Results Box:
        Displayed only when results are availabled.

        It provides 4 different sections that are visible only if the method
        associated to fill them has been implemented:

        * A Result box: Shows the results of the stage. Subclass must implement
          :meth:`_buildResultsStage`.
        * A Setting collapsible box: Shows the settings used for the stage.
          Subclass must implement :meth:`_buildResultsSetting`.
        * A Plot collapsible box: Shows buttons to open the stage analysis
          plots. Subclass must implement :meth:`_buildResultsPlots`.
        * A Result Table collapsible box: Show the results per sequence or per
          triplet under the form of a table. Subclass must implement
          :meth:`_buildResultsTripletsTable`.
        * A open result dir button: Open the directory containing the results.
          The subclass do not need to implement anything.

        Results are expected to be updated when the IOPGM associated with the
        phase emits it's signal :any:`IOPhaseGuiManager.stateChanged`. In this
        case, the :meth:`_loadResults` method will be called. It must be
        implemented by the subclass. This method wil also be called after
        object initialization.
    """

    def __init__(
        self, stage: str, iopm: IOPhaseGuiManager, *args,
        showProgress: bool = False, **kwargs
    ) -> None:
        """ Constructor.

        Args:
            stage (str): Name of the stage. Used to retrieve stage parameters.
            iopm (IOPhaseGuiManager): IOPhaseGuiManager to use.
            showProgress (bool): Whether or not to connect to the progress
                signal of the runner to display progress.
        """
        super().__init__(*args, **kwargs)
        self._iopm = iopm
        self._stage = stage
        self._showProgress = showProgress

        # ScrollArea
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)

        # Widget associated with the area
        self._mainWidget = QWidget(parent=self)
        self._mainWidget.setBackgroundRole(QPalette.ColorRole.Base)
        self.setWidget(self._mainWidget)

        # Setup the calculator runner
        self._runner = CalculatorRunner()
        self._runner.finished.connect(self._stopCompute)
        self._runner.runAvailable.connect(self._setCalculatorAvailable)
        self._runner.runDisabled.connect(self._setCalculatorDisabled)
        self._calculatorAvailable = True
        self._buttonLoading = False

        # Build the Gui
        self._mainLayout = QVBoxLayout()
        self._mainWidget.setLayout(self._mainLayout)
        self._mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        settingsBox = QGroupBox('Settings', parent=self._mainWidget)
        settingsLayout = self._buildSettings(settingsBox)
        settingsBox.setLayout(settingsLayout)
        self._mainLayout.addWidget(settingsBox)
        self._buildRunButton()
        self._buildResults()

        # Populate settings and load previous results
        self._safeUpdateSettings()
        self._updateRunButton()
        self._updateResults()
        self._iopm.stateChanged.connect(self._safeUpdateSettings)
        self._iopm.stateChanged.connect(self._updateRunButton)
        self._iopm.stateChanged.connect(self._updateResults)

    @abc.abstractmethod
    def _buildSettings(self, parent: QWidget) -> QLayout:
        """ Create the settings QLayout that will be added to the top of the
        widget layout.

        Args:
            parent(QWidget): Parent widget for all widget created here.

        Returns:
            QLayout: Settings layout created.
        """
        pass

    def _buildRunButton(self) -> None:
        """ Build the button that trigger the run of the computation.
        """
        # Run Button
        self._runButton = QPushButton(parent=self._mainWidget)
        self._runButton.clicked.connect(self._startCompute)
        self._mainLayout.addWidget(self._runButton)

        self._loadingLayout: LoadingAnimationLayout | LoadingProgressLayout
        if not self._showProgress:
            # LoadingAnimationLayout
            self._loadingLayout = LoadingAnimationLayout(
                parent=self._runButton)
            self._runButton.setLayout(self._loadingLayout)
        else:
            # LoadingProgressLayout
            self._loadingLayout = LoadingProgressLayout(
                parent=self._runButton)
            self._runButton.setLayout(self._loadingLayout)
            self._runner.progress.connect(self._loadingLayout.setProgress)

    def _buildResults(self) -> None:
        """ Create the results QLayout that will be added to the bottom of
        the widget layout.

        Returns:
            QLayout: Results layout created.
        """
        # Main Box
        self._resultsBox = QGroupBox('Results', parent=self._mainWidget)
        self._mainLayout.addWidget(self._resultsBox)
        resultsLayout = QVBoxLayout()
        self._resultsBox.setLayout(resultsLayout)

        # Stage Results box
        title = self._stage.capitalize()
        if len(title) <= 4:
            title = title.upper()
        stageResultBox = QGroupBox(title, parent=self._resultsBox)
        stageResultBox.setStyleSheet('QGroupBox { font-weight: bold; }')
        stageResultLayout = self._buildResultsStage(stageResultBox)
        if stageResultLayout is not None:
            resultsLayout.addWidget(stageResultBox)
            stageResultBox.setLayout(stageResultLayout)
        else:
            stageResultBox.setParent(None)

        # Settings box
        settingsBox = CollapsibleBox('Settings', parent=self._resultsBox)
        settingsLayout = self._buildResultsSetting(settingsBox)
        if settingsLayout is not None:
            resultsLayout.addWidget(settingsBox)
            settingsBox.addContentLayout(settingsLayout)
        else:
            settingsBox.setParent(None)

        # Plot box
        plotBox = CollapsibleBox('Plots', parent=self._resultsBox)
        plotLayout = self._buildResultsPlots(plotBox)
        if plotLayout is not None:
            resultsLayout.addWidget(plotBox)
            plotBox.addContentLayout(plotLayout)
        else:
            plotBox.setParent(None)

        # Plot box
        if self._stage == 'fret':
            title = 'Triplets'
        else:
            title = 'Sequences'
        tripletTableBox = CollapsibleBox(title, parent=self._resultsBox)
        tripletTableLayout = self._buildResultsTripletsTable(tripletTableBox)
        if tripletTableLayout is not None:
            resultsLayout.addWidget(tripletTableBox)
            tripletTableBox.addContentLayout(tripletTableLayout)
        else:
            tripletTableBox.setParent(None)

        # OpenDirButton
        openDirButton = QPushButton('Open Directory', parent=self._resultsBox)
        openDirButton.clicked.connect(self._openResultsDir)
        openDirButton.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        openDirButton.setToolTip(
            f'Open the {self._stage.upper()} output dir in your file manager.'
        )
        resultsLayout.addWidget(openDirButton)

    def _buildResultsStage(self, parent: QWidget) -> QLayout | None:
        """ Create the layout that will hold the results of the Stage. If None
        is returned, will not create this box.

        Args:
            parent(QWidget): Parent widget for all widget created here.

        Returns:
            QLayout | None: Results layout created.
        """
        return None

    def _buildResultsSetting(self, parent: QWidget) -> QLayout | None:
        """ Create the layout that will hold the settings used to compute
        the results. If None is returned, will not create this box.

        Args:
            parent(QWidget): Parent widget for all widget created here.

        Returns:
            QLayout | None: Results layout created.
        """
        return None

    def _buildResultsPlots(self, parent: QWidget) -> QLayout | None:
        """ Create the layout that will hold the stage plots buttons. If None
        is returned, will not create this box.

        Args:
            parent(QWidget): Parent widget for all widget created here.

        Returns:
            QLayout | None: Results layout created.
        """
        return None

    def _buildResultsTripletsTable(self, parent: QWidget) -> QLayout | None:
        """ Create the layout that will hold the results triplet table. If None
        is returned, will not create this box.

        Args:
            parent(QWidget): Parent widget for all widget created here.

        Returns:
            QLayout: Results layout created.
        """
        return None

    def _safeUpdateSettings(self) -> None:
        """ Update the settings widgets while preventing the signals to be
        raised by them for value changed.

        Will be called on :any:`IOGuiManager.stateChanged` Signal.
        """
        self._blockAllSignals(True)
        self._updateSettings()
        self._blockAllSignals(False)

    def _blockAllSignals(self, val: bool) -> None:
        """ Call the `blockSignal` method of all widget whose signal is
        connected to a slot.

        The purpose of this method is to prevent slots to call config set
        while being updated by it.

        This is expected to be overriden.

        Args:
            val (bool): The value to pass to the `blockSignal` method.
        """
        pass

    @abc.abstractmethod
    def _updateSettings(self) -> None:
        """ Update the settings widgets.

        Will be called on :any:`IOGuiManager.stateChanged Signal.
        """
        pass

    def _updateRunButton(self) -> None:
        """ Update the Run button widget.
        """
        if not self._buttonLoading:
            try:
                series = self._iopm.params.get(self._stage)[1]
                text = f'Run on {series.size} sequences'
                enable = True
            except QtfException as e:
                text = f'Impossible to run: {e}'
                enable = False
            self._runButton.setEnabled(enable)
            self._runButton.setText(text)

            if not self._calculatorAvailable:
                self._runButton.setEnabled(False)

    def _updateResults(self) -> None:
        """ Update the results widgets.
        """
        if self._loadResults():
            self._resultsBox.show()
        else:
            self._resultsBox.hide()

    @abc.abstractmethod
    def _loadResults(self) -> bool:
        """ Load the results, update the results widget. and inform if results
        were found.

        Returns:
            bool: True if results were loaded, False otherwise.
        """
        pass

    def _startCompute(self) -> None:
        """ Start the worker that will perdorm the computation, disable the
        button and starts the loading animation.
        """
        # Disable the button
        self._buttonLoading = True
        self._runButton.setEnabled(False)

        # Hide previous results
        self._resultsBox.hide()

        # Start loading animation
        self._runButton.setText("")
        self._loadingLayout.start()

        # Run computation
        self._runner.run(self._stage)

    def _stopCompute(self, stage: str) -> None:
        """ If the stage match the one of the widget, stops the loading
        animation, and restores the button.

        Args:
            stage (str): Stage that finished the run.
        """
        if stage == self._stage:
            # Stop loading animation
            self._loadingLayout.stop()

            # Restore button
            self._buttonLoading = False
            self._updateRunButton()

    def _setCalculatorAvailable(self) -> None:
        """ Set the calculator to available state.
        """
        self._calculatorAvailable = True
        self._updateRunButton()

    def _setCalculatorDisabled(self) -> None:
        """ Set the calculator to disabled state.
        """
        self._calculatorAvailable = False
        self._updateRunButton()

    def _str_val(self, value: Any) -> str:
        """ Return the str representation of a value or ``''`` if ``None``.
        """
        return str(value) if value is not None else ' -'

    def _openResultsDir(self) -> None:
        """ Open the results directory.
        """
        dir = self._iopm.results[self._stage].output_dir
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(dir)))
