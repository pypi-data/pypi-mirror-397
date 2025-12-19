from quanti_fret.algo import BackgroundMode
from quanti_fret.apps.gui.io_gui_manager import IOGuiManager

from qtpy.QtWidgets import QRadioButton


class BckgModeRadioButton(QRadioButton):
    """ Radio Button representing a :any:`BackgroundMode`.

    This class is responsible to save the new background mode to the config
    when clicked and to update itself when a config changed.
    """
    def __init__(
        self, phase: str, mode: BackgroundMode, *args, **kwargs
    ) -> None:
        """Constructor.

        Args:
            phase (str): Phase of the widget.
            mode (BackgroundMode): Mode associated with the button.
        """
        super().__init__(f'{mode}', *args, **kwargs)
        self._iopm = IOGuiManager().get_iopm(phase)
        self._mode = mode
        self._nbSequences = 0
        self.toggled.connect(self.switchMode)
        self._iopm.stateChanged.connect(self._updateSettings)

        self._updateSettings()

    @property
    def mode(self) -> BackgroundMode:
        """ Mode associated with this button.
        """
        return self._mode

    def switchMode(self, checked: bool) -> None:
        """ Set in the config this button's mode if ``checked`` is set to
        ``True``.

        Args:
            checked (bool): Whether or not the button is checked.
        """
        if checked:
            self._iopm.config.set('Background', 'mode', self.mode)

    def _updateSettings(self) -> None:
        """ Update this button with the valu from the config..
        """
        self.blockSignals(True)
        # Set config mode
        current_mode = self._iopm.config.get('Background', 'mode')
        if current_mode == self.mode:
            self.setChecked(True)
        else:
            self.setChecked(False)
        self.blockSignals(False)
