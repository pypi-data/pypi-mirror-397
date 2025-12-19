from quanti_fret.core import QtfException
from quanti_fret.io.base.validate.validators import Validator

from typing import Any


class BooleanValidator(Validator):
    """ Validator for ``bool`` values.

    Data from the format must respect:

    * Input types:

      * *Ini*: ``str``. Values are case insensitive ``"True"`` and ``"False"``.
      * *Json*: ``bool``.

    API types are:

    * *convert_from*: returns a ``bool``.
    * *convert_to*: accepts a ``bool``.
    """

    def __init__(self) -> None:
        """ Constructor.
        """
        super().__init__(str, bool)

    def _validate(self, format: str, value: Any) -> None:
        if format == 'ini':
            # value is str
            if value.lower() not in ['true', 'false']:
                error = f'"{value}" should be "true" or "false"'
                raise QtfException(error)

    def _convert_from_format(self, format: str, value: Any) -> Any:
        if format == 'ini':
            # value is str
            if value.lower() == 'true':
                return True
            else:
                return False
        else:
            # value is bool
            return value

    def _convert_to_format(self, format: str, value: Any) -> Any:
        if not isinstance(value, bool):
            raise QtfException(f'Value {value} is not a bool')
        return value
