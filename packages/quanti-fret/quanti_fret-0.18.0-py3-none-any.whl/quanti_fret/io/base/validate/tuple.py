from quanti_fret.core import QtfException
from quanti_fret.io.base.validate.validators import Validator

from typing import Any


class TupleValidator(Validator):
    """ Validator for ``tuple`` values.

    It is linked with another :any:`Validator` to validate each element of the
    Tuple.

    Data from the format must respect:

    * Input types:

      * *Ini*: ``str``, and values are separated by a coma.
      * *Json*: ``tuple``.
    * Each value of the ``tuple`` pass the validation of the element validator.
    * If set, the ``tuple`` size is the one expected by the ``TupleValidator``.

    API types are:

    * *convert_from*: returns a ``tuple[element validator type]``.
    * *convert_to*: accepts ``tuple`` or ``list`` of
      ``element validator type``.
    """

    def __init__(self, element_validator: Validator, size: int = -1) -> None:
        """ Constructor.

        Args:
            element_validator (Validator): Validator used to validate / convert
                all the elements of the ``tuple``.
            size (int, optional): Expected size of the validator. If ``-1``,
                allows all size. Default is ``-1``.
        """
        super().__init__(str, [tuple, list])
        self._element_validator = element_validator
        self._size = size

    def _validate(self, format: str, value: Any) -> None:
        """ Validate that the value passed is valid.

        If `self.size` > 0, check that the size of the tuple is correct. Then
        validate all elements of the tuple with `self._element_validator`.

        Args:
            format (str): Whether the value comes from ``ini`` or ``json``
                file.
            value (str): Value loaded and cast.

        Raises:
            QtfException: The value is not valid.
        """
        if format == "ini":
            value = self._convert_str_to_tuple(value)
            validator = self._element_validator.validate_from_ini
        else:
            validator = self._element_validator.validate_from_json

        # value is Tuple
        if self._size > 0 and len(value) != self._size:
            err = f'Invalid tuple size. Got {len(value)}, expected ' \
                  f'{self._size}'
            raise QtfException(err)
        for val in value:
            validator(val)

    def _convert_from_format(self, format: str, value: Any) -> Any:
        """ Convert the value loaded from the given format into the type
        expected in the quanti_fret module.

        Calls `self._element_validator` to convert each elements of the tuple.

        Args:
            format (str): Whether the value comes from ``ini`` or ``json``
                file.
            value (str): Value loaded and cast.

        returns:
            Any: value converted in the type expected in the quanti_fret
                module, or None if the value is empty.
        """
        if format == "ini":
            value = self._convert_str_to_tuple(value)
            convertor = self._element_validator.convert_from_ini
        else:
            convertor = self._element_validator.convert_from_json

        # value is Tuple
        ret = [convertor(val) for val in value]
        return tuple(ret)

    def _convert_to_format(self, format: str, value: Any) -> Any:
        """ Convert the value comming from the quanti_fret module into a type
        understood by the targeted format.

        Calls `self._element_validator` to convert each elements of the tuple.
        If `self.size` > 0, check that the size of the tuple is correct.

        Args:
            format (str): Whether the value comes from ``ini`` or ``json``
                file.
            value (str): Value loaded and cast.

        Raises:
            QtfException: The value is not valid.

        returns:
            Any:
                A representation of the value in a format understood by the
                target file format. For ``ini``, it is expected to be castable
                to ``string``.
        """
        if type(value) is list:
            value = tuple(value)
        if type(value) is not tuple:
            raise QtfException(f'{value} is not a tuple')

        # value is Tuple
        if self._size > 0 and len(value) != self._size:
            err = f'Invalid tuple size. Got {len(value)}, expected ' \
                  f'{self._size}'
            raise QtfException(err)

        if format == 'ini':
            convertor = self._element_validator.convert_to_ini
        else:
            convertor = self._element_validator.convert_to_json

        ret = [convertor(val) for val in value]
        if format == "ini":
            return ', '.join(ret)
        else:
            return ret

    def _convert_str_to_tuple(self, val: str) -> tuple[Any, ...]:
        """Convert a string tuple to a python tuple.

        Input is expected to be a string, with each values sepratated by comas.

        Args:
            val (str): Value to transform.

        Returns:
            tuple[Any, ...]: Tuple from the value.
        """
        if val == '':
            return ()
        else:
            return tuple(val.split(','))
