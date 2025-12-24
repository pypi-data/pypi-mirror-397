from quanti_fret.core import QtfException
from quanti_fret.io.base.validate.validators import Validator

from typing import Any


class StringValidator(Validator):
    """ Simple ``string`` validator.

    Data from the format must respect:

    * Input types:

      * *Ini*: ``str``.
      * *Json*: ``str``.

    API types are:

    * *convert_from*: returns a ``str``.
    * *convert_to*: accepts a ``str``.
    """

    def __init__(self) -> None:
        """ Constructor.
        """
        super().__init__(str, str)

    def _convert_to_format(self, format: str, value: Any) -> Any:
        if type(value) is not str:
            raise QtfException(f'{value} is not a str')

        return value
