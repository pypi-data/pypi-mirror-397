from quanti_fret.core import QtfException

from typing import Any


class Validator:
    """ Provide the interface for the validation and convertion of values
    comming from or going to ``ini`` or ``json`` formats.

    This class is designed to be inherited for every type of values that you
    want to validate and convert.

    For the validation part, this class starts by trying to cast the value to
    an intermediate format. Then it delegates its validation to the subclass
    through the :meth:`_validate` method.

    Note that the intermediate type used to cast the input value can be
    different from the final type used in the ``quanti_fret`` module. For
    example, a background mode is an ``int`` in the ``ini`` and ``Json``
    format, but an ``Enum`` in the module.

    To create a :class:`Validator`, in addition to the ``ini_cast_type`` and
    ``json_types`` parameters to pass to the constructor, you need to
    implement:

    * :meth:`validate`: Method that validate if the value match your custom
      criterias after being cast.
    * :meth:`_convert_from_format`: Method that convert the value comming
      from the given format into the type used in the ``quanti_fret`` module.
    * :meth:`_convert_to_format`: Method that convert the value comming from
      the ``quanti_fret`` module into a value serializable into the given
      format.
    """

    def __init__(
        self, ini_cast_type: type, json_types: type | list[type]
    ) -> None:
        """ Constructor.

        Args:
            ini_cast_type (type): Intermediate type to use to cast data from
                ``ini`` files, to perform validation and convertion later on.
            json_types (type | list[type]): List of types that you expect to
                find in the json format. The first one is used to cast the
                value before validation and convertion.
        """
        super().__init__()
        self._ini_cast_type = ini_cast_type
        self._json_type: list[type]
        if type(json_types) is not list:
            self._json_type = [json_types]  # type: ignore
        else:
            self._json_type = json_types

    def validate_from_ini(self, value: str) -> None:
        """ Validate that the value loaded from an ``ini`` file is valid.

        It first checks if the value can be casted into the ``ini_cast_type``
        type, then it delegates the validation to the :meth:`_validate` method.

        Args:
            value (str): Value returned by the config parser.

        Raises:
            QtfException: The value is not valid.
        """
        # Check type
        try:
            casted_value = self._ini_cast_type(value)
        except ValueError:
            error = f'Bad type: "{value}" is not a valid ' \
                    f'"{str(self._ini_cast_type)}"'
            raise QtfException(error)

        # Run value check
        self._validate('ini', casted_value)

    def validate_from_json(self, value: Any) -> None:
        """ Validate that the value loaded from a ``json`` file is valid.

        It first checks if the value has one of the expected type from
        ``json_types``, then it delegates the validation to the
        :meth:`_validate` method.

        Args:
            value (Any): Value returned by the ``json`` loader.

        Raises:
            QtfException: The value is not valid.
        """
        # Check type
        found = False
        for t in self._json_type:
            if type(value) is t:
                found = True
                break
        if not found:
            error = f'Bad type: "{value}" is not a valid ' \
                    f'"{str(self._json_type)}"'
            raise QtfException(error)

        # Run value check
        self._validate('json', value)

    def convert_from_ini(self, value: str) -> Any:
        """ Convert the value loaded from the ``ini`` file into the type
        expected in the ``quanti_fret`` module.

        No validation is done here, we expect that the value is already
        validated.

        Args:
            value (str): Value returned by the config parser.

        returns:
            Any:
                Value converted in the type expected in the ``quanti_fret``
                module.
        """
        return self._convert_from_format('ini', self._ini_cast_type(value))

    def convert_from_json(self, value: str) -> Any:
        """ Convert the value loaded from the ``json`` file into the type
        expected in the ``quanti_fret`` module.

        No validation is done here, we expect that the value is already
        validated.

        Args:
            value (str): Value returned by the ``json`` loader.

        returns:
            Any:
                Value converted in the type expected in the ``quanti_fret``
                module.
        """
        return self._convert_from_format('json', self._json_type[0](value))

    def convert_to_ini(self, value: Any) -> str:
        """ Convert the value comming from the ``quanti_fret`` module into a
        ``str`` to put in the ``ini`` file.

        Args:
            value (Any): Value to set to the ``ini`` file.

        Raises:
            QtfException: The value is not valid.

        returns:
            str:
                A string representation of the value to set in the ``ini``
                file.
        """
        return str(self._convert_to_format('ini', value))

    def convert_to_json(self, value: Any) -> Any:
        """ Convert the value comming from the ``quanti_fret`` module into a
        type serializable into a ``json``.

        Args:
            value (Any): Value to prepare for serialization.

        Raises:
            QtfException: The value is not valid.

        returns:
            Any: Object serializable into a ``json`` format.
        """
        return self._convert_to_format('json', value)

    def _validate(self, format: str, value: Any) -> None:
        """ Validate that the value passed is valid.

        Args:
            format (str): Whether the value comes from ``ini`` or ``json``
                file.
            value (str): Value loaded and cast.

        Raises:
            QtfException: The value is not valid.
        """
        pass

    def _convert_from_format(self, format: str, value: Any) -> Any:
        """ Convert the value loaded from the given format into the type
        expected in the quanti_fret module.

        Args:
            format (str): Whether the value comes from ``ini`` or ``json``
                file.
            value (str): Value loaded and cast.

        returns:
            Any: value converted in the type expected in the quanti_fret
                module, or None if the value is empty.
        """
        return value

    def _convert_to_format(self, format: str, value: Any) -> Any:
        """ Convert the value comming from the quanti_fret module into a type
        understood by the targeted format.

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
        return value
