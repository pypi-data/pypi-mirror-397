from qtpy.QtWidgets import QDoubleSpinBox


class PercentileSpinBox(QDoubleSpinBox):
    """ SpinBox for percentile values.

    Values are between ``0`` and ``100``, and the step is ``1``.

    It also add the suffix ``%``.
    """
    def __init__(self, *args, **kwargs):
        """ Constructor
        """
        super().__init__(*args, **kwargs)
        self.setRange(0.0, 100.0)
        self.setSingleStep(1.)
        self.setSuffix('%')
