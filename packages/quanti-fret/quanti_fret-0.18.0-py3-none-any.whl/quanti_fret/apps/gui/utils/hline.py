from qtpy.QtWidgets import QFrame


class HLine(QFrame):
    """ Horizontal Grey Line to separate sections.

    Overengineered but Napari was not very compliant with me when using a
    regular ``QFrame`` with ``HLine`` shape.
    """
    def __init__(self, *args, **kwargs) -> None:
        """Constructor.
        """
        super().__init__(*args, **kwargs)

        color = 'rgb(124, 124, 124)'

        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet(f'color: {color}; background-color: {color};')
        self.setFixedHeight(1)
