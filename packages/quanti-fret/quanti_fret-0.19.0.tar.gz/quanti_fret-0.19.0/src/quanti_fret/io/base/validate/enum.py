from quanti_fret.core import QtfException
from quanti_fret.io.base.validate.validators import Validator

from enum import Enum
from typing import Any


class EnumValidator(Validator):
    """ Validator for ``Enum`` values.

    * Input types:

      * *Ini*: ``int``.
      * *Json*: ``int``.
    * The integer value must be in the range of the ``Enum`` class values.

    API types are:

    * *convert_from*: returns the ``Enum`` type passed to the constructor.
    * *convert_to*: accepts the ``Enum`` type passed to the constructor.
    """

    def __init__(self, enum_class: type) -> None:
        """ Constructor.

        Args:
            enum_class (type): Enum class represented by the
                :class:`EnumValidator`.
        """
        super().__init__(int, int)
        assert issubclass(enum_class, Enum)
        self._enum_class = enum_class

    def _validate(self, format: str, value: Any) -> None:
        """ Validate that the value passed is valid.

        A valid value is in the range of the ``Enum`` values.

        Args:
            format (str): Whether the value comes from ``ini`` or ``json``
                file.
            value (str): Value loaded and cast.

        Raises:
            QtfException: The value is not valid.
        """
        # value is int
        min = 0
        max = len(self._enum_class) - 1
        if value < min or value > max:
            error = f'"{value}" is not a valid mode (0-{max})'
            raise QtfException(error)

    def _convert_from_format(self, format: str, value: Any) -> Any:
        # value is int
        return self._enum_class(value)

    def _convert_to_format(self, format: str, value: Any) -> Any:
        if not isinstance(value, self._enum_class):
            err = f'Value "{value}" is not a {self._enum_class.__name__}'
            raise QtfException(err)
        return value.value
