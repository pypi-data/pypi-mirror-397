from quanti_fret.algo.gamma.calculator import GammaCalculator


class BTCalculator(GammaCalculator):
    """ :any:`GammaCalculator` implementation for the BleedThrough.

    Computes the :math:`\\alpha^{BT}` value.
    """

    def __init__(self) -> None:
        """Constructor.
        """
        super().__init__('alpha_BT', 'DD')

    def _get_gamma_channels_index(self) -> int:
        """ Return the gama channels index associated with the given sequence.

        Returns:
            int: The gamma channels index.
        """
        return 0

    def _get_gamma_plot_params(self) -> tuple[tuple[float, float], int]:
        """ Get the range and nticks params to give to the function that plot
        the gamma image.

        Args:
            seq (TripletSequence): The associated sequence.

        Returns:
            tuple[tuple[float, float], int]: range, nticks.
        """
        return (0.1, 0.9), 9
