from quanti_fret.core import QtfException, QtfSeries


class QtfSeriesManager:
    """ Allows getting and settings the different :any:`QtfSeries` used in a
    phase.

    usage:

    .. code:: Python

        series = series_manager.get('my_series')
        series_manager.set('my_series', new_series)
        # ...

    """
    def __init__(self, series_name: list[str]) -> None:
        """ Constructor.

        Args:
            series_name (list[str]): The list of series names accepted.
        """
        self._series: dict[str, QtfSeries] = {}
        for name in series_name:
            self._series[name] = QtfSeries([])

    def set(self, name: str, series: QtfSeries) -> None:
        """ Set the given series.

        Args:
            name (str): The name of the series to set.
            series (QtfSeries): The series object to set.

        Raises:
            QtfException: if the name is not valid.
        """
        if name not in self._series.keys():
            raise QtfException(f'Unknown series "{name}"')
        self._series[name] = series

    def get(self, name: str | list[str]) -> QtfSeries:
        """ Get the series associated with the given name, or concatenate
        mutliple series if multiple names are asked.

        Args:
            name (str): Series name or list of series name to get.

        Raises:
            QtfException: One name is not valid.

        Returns:
            QtfSeries: The series associated.
        """
        if type(name) is str:
            name = [name]

        series = QtfSeries([])
        for key in name:
            if key not in self._series.keys():
                raise QtfException(f'Unknown series "{key}"')
            series += self._series[key]
        return series
