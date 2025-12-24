from quanti_fret.algo import (
    BackgroundEngine, BackgroundEngineFixed, BackgroundEnginePercentile,
    BackgroundMode, create_background_engine
)

from quanti_fret.core import QtfException
from quanti_fret.io.base.validate.enum import EnumValidator
from quanti_fret.io.base.validate.float import FloatValidator
from quanti_fret.io.base.validate.tuple import TupleValidator
from quanti_fret.io.base.validate.validators import Validator

from typing import Any


class BackgroundEngineValidator(Validator):
    """ Validator for ``BackgroundEngine`` values.

    .. important::

        For now, this is not compatible with ``Ini`` format.

    Data from the format must respect:

    * Input types:

      * *Ini*: ``str`` (But will fail validation).
      * *Json*: ``dict``.
    * The value inside the dict at least the ``'mode'`` key.
    * For ``Percentile`` mode, the dict contains the ``'percentile'`` key.
    * For ``Fixed`` mode, the dict contains the ``'value'`` key.

    API types are:

    * *convert_from*: returns a :any:`BackgroundEngine`.
    * *convert_to*: accepts a :any:`BackgroundEngine`.
    """

    def __init__(self) -> None:
        """ Constructor
        """
        super().__init__(str, dict)
        self._background_mode_validator = EnumValidator(BackgroundMode)
        self._percentile_validator = FloatValidator(min=0., max=100.)
        self._fixed_validator = TupleValidator(FloatValidator(min=0.), size=3)

    def _validate(self, format: str, value: Any) -> None:
        if format == "ini":
            err = 'BackgroundEngineResultsValidator is not implemented for ini'
            raise QtfException(err)

        if type(value) is not dict:
            err = f'Invalid Background engine type for {value}. Expected dict'
            raise QtfException(err)

        if 'mode' not in value:
            err = 'Missing key "mode" for the background engine'
            raise QtfException(err)

        self._background_mode_validator.validate_from_json(value['mode'])
        mode = self._background_mode_validator.convert_from_json(value['mode'])
        if mode == BackgroundMode.PERCENTILE:
            if 'percentile' not in value:
                err = 'Missing key "percentile" for the background engine'
                raise QtfException(err)
            self._percentile_validator.validate_from_json(value['percentile'])
        elif mode == BackgroundMode.FIXED:
            if 'value' not in value:
                err = 'Missing key "value" for the background engine'
                raise QtfException(err)
            self._fixed_validator.validate_from_json(value['value'])

    def _convert_from_format(self, format: str, value: Any) -> Any:
        if format == "ini":
            raise QtfException('TupleValidator is not implemented for ini')

        # Automatic converter transforms 'disabled' into ('d', 'i', 's', ...)
        mode = self._background_mode_validator.convert_from_json(value['mode'])
        percentile = -1
        background = None
        if mode == BackgroundMode.PERCENTILE:
            percentile = self._percentile_validator.convert_from_json(
                value['percentile']
            )
        elif mode == BackgroundMode.FIXED:
            background = self._fixed_validator.convert_from_json(
                value['value']
            )
        return create_background_engine(mode, background, percentile)

    def _convert_to_format(self, format: str, value: Any) -> Any:
        if format == "ini":
            raise QtfException('TupleValidator is not implemented for ini')

        if not isinstance(value, BackgroundEngine):
            err = f'Value {value} is not a Background Engine'
            raise QtfException(err)

        mode = value.mode
        ret = {}
        ret['mode'] = self._background_mode_validator.convert_to_json(mode)
        if isinstance(value, BackgroundEnginePercentile):
            ret['percentile'] = \
                self._percentile_validator.convert_to_json(
                    value._percentile
                )
        elif isinstance(value, BackgroundEngineFixed):
            ret['value'] = self._fixed_validator.convert_to_json(
                value.background
            )

        return ret


class BackgroundResultsValidator(Validator):
    """ Validator for Background Results values.

    This handle the saving of the Background stage.

    When loading the stage's result, it will create:

    * A :any:`BackgroundEngineFixed` if the value is a background tuple.
    * A :any:`BackgroundEngineDisabled` if the value is 'disabled'.

    .. important::

        For now, this is not compatible with ``Ini`` format.

    Data from the format must respect:

    * Input types:

      * *Ini*:  ``str`` (But will fail validation)
      * *Json*: ``tuple`` or a ``str``
    * If a ``tuple``, the size must be 3, and the values must be ``float``.
    * If a ``str``, it must be ``"Disabled"``.

    API types are:

    * *convert_from*: returns a ``BackgroundEngine``.
    * *convert_to*: accepts a ``tuple[float, float, float]`` or ``None`` if
      disabled.
    """

    def __init__(self) -> None:
        """ Constructor.
        """
        super().__init__(str, [tuple, list, str])
        self._tuple_validator = TupleValidator(FloatValidator(min=0), 3)

    def _validate(self, format: str, value: Any) -> None:
        if format == "ini":
            err = 'BackgroundEngineResultsValidator is not implemented for ini'
            raise QtfException(err)

        if type(value) is str:
            if value != 'disabled':
                err = f'Unknown Background Results {value}. Expected a tuple' \
                      ' or "disabled".'
                raise QtfException(err)
        elif type(value) is tuple or type(value) is list:
            self._tuple_validator.validate_from_json(value)
        else:
            err = 'Invalid Background Results type'
            raise QtfException(err)

    def _convert_from_format(self, format: str, value: Any) -> Any:
        if format == "ini":
            raise QtfException('TupleValidator is not implemented for ini')

        # Automatic converter transforms 'disabled' into ('d', 'i', 's', ...)
        if len(value) == 8 and type(value[0]) is str:
            return create_background_engine(mode=BackgroundMode.DISABLED)
        else:
            background = self._tuple_validator.convert_from_json(value)
            return create_background_engine(mode=BackgroundMode.FIXED,
                                            background=background)

    def _convert_to_format(self, format: str, value: Any) -> Any:
        if format == "ini":
            raise QtfException('TupleValidator is not implemented for ini')

        if value is None:
            return 'disabled'

        return self._tuple_validator.convert_to_json(value)
