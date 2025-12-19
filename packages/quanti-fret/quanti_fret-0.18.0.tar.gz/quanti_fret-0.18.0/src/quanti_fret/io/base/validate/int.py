from quanti_fret.core import QtfException
from quanti_fret.io.base.validate.validators import Validator

from typing import Any

import numpy as np


class IntValidator(Validator):
    """ Simple ``int`` validator.

    Data from the format must respect:

    * Input types:

      * *Ini*: ``int``.
      * *Json*: ``int``.
    * If set, the value must be greater or equals to the minimum.
    * If set, the value must be lower or equals to the maximum.

    API types are:

    * *convert_from*: returns an ``int``.
    * *convert_to*: accepts an ``int`` or a ``np.integer``.
    """

    def __init__(
        self, min: int | None = None, max: int | None = None
    ) -> None:
        """ Constructor.

        Args:
            min (int | None, optional): If not ``None``, set the minimum value
                accepted. Default is ``None``.
            max (int | None, optional): If not ``None``, set the maximum value
                accepted. Default is ``None``.
        """
        super().__init__(int, int)
        self._min = min
        self._max = max

    def _validate(self, format: str, value: Any) -> None:
        """ Validate that the value passed is valid.

        If set in the constructor, Value must be between self._min and
        self._max.

        Args:
            format (str): Whether the value comes from ``ini`` or ``json``
                file.
            value (str): Value loaded and cast.

        Raises:
            QtfException: The value is not valid.
        """
        # value is int
        if self._min is not None:
            if value < self._min:
                error = f'"{value}" is below the min "{self._min}"'
                raise QtfException(error)
        if self._max is not None:
            if value > self._max:
                error = f'"{value}" is above the max "{self._max}"'
                raise QtfException(error)

    def _convert_to_format(self, format: str, value: Any) -> Any:
        if isinstance(value, np.integer):
            value = int(value)
        if type(value) is not int:
            raise QtfException(f'{value} is not an int')

        self._validate(format, value)

        if format == 'ini':
            return str(value)
        else:
            return value
