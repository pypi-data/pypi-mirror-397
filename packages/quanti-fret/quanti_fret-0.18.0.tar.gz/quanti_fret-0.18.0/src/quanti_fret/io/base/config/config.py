from quanti_fret.core import QtfException
from quanti_fret.io.base.config.exception import QtfConfigException
from quanti_fret.io.base.validate import Validator

from typing import Any
import configparser
import os


class Config:
    """ Manage the Quanti-FRET configuration.

    The format expected is the ``ini`` format.

    This class uses the ``configparser`` modules, and adds the following
    features:

    * Validation of the content of the config.
    * Formatting of the config values from and to their real type in the
      quantifret module.
    * Adding default values.

    The validation and convertion are done with the following system:

    * This class is initiated with a dictionnary representing all the expected
      sections and keys of the config. For each key is associated a
      :any:`Validator` class, and a default value.
    * When loading a config file, we check that each section and key is
      present, and we validate them calling the
      :any:`Validator.validate_from_ini` method of each key's validator.
    * To get the converted value of a key, you need to call the :meth:`get`
      method. It will, itself check if the section and key are valid, and call
      the :any:`Validator.convert_from_ini` method associated.
    * To set the converted value of a key, you need to call the :meth:`set`
      method. It will, itself check if the section and key are valid, and call
      the :any:`Validator.convert_to_ini` method associated.

    usage:

    .. code::

       config = Config()
       config.load(file)
       value = config.get("section", "key")
       config.set("section", "key", new_val)
       config.save(file)
    """
    def __init__(
        self, validators: dict[str, dict[str, tuple[Validator, str]]]
    ) -> None:
        """Constuctor.

        Args:
            validators (dict[str, dict[str, tuple[Validator, str]]]):
                Validators to use to validate the config and converts the
                values.
        """
        self._parser = configparser.ConfigParser(allow_no_value=True)
        self._validators = validators
        self._valid_config = False

    def load(
        self, filename: os.PathLike | str, accept_missing_keys: bool = False
    ) -> None:
        """ Read, load and validate the configuration file passed as parameter.

        Args:
            filename (os.PathLike | str): Path to the ini config file.
            accept_missing_keys (bool, optional): If set to True, the
                validation will accept missing keys and set them to their
                default value. Default to ``False``.

        Raises:
            QtfConfigException: If the configuration is not valid.
        """
        self._valid_config = False
        try:
            ret = self._parser.read(filename)
        except configparser.Error as e:
            error = f'Bad ini format for "{filename}": {e}'
            raise QtfConfigException(error)
        if ret is None or len(ret) == 0:
            error = f'File not found or not read: "{filename}"'
            raise QtfConfigException(error)
        self._validate(accept_missing_keys=accept_missing_keys)
        self._valid_config = True

    def save(self, filename: os.PathLike | str) -> None:
        """ Save the configuration into the file passed as parameter.

        Args:
            filename (os.PathLike | str): Path to the file to write.
        """
        with open(filename, 'w') as f:
            self._parser.write(f)

    def set_default(self):
        """ Set the config to its default values.
        """
        for section, keys in self._validators.items():
            self._parser[section] = {}
            for key, settings in keys.items():
                self._parser[section][key] = settings[1]
        self._valid_config = True

    def get(self, section: str, key: str) -> Any:
        """ Get a value from the config file converted to the type used in
        the module.

        Args:
            section (str): Section of the key.
            key (str): Key of the value to get.

        Raises:
            QtfConfigException: If no config is loaded, or if the section or
                key do not exists.

        Returns:
            Any: The converted object matching the section/value.
        """
        if not self._valid_config:
            error = 'No valid config loaded'
            raise QtfConfigException(error)
        if section not in self._parser:
            error = f'Unknown section: "[{section}]"'
            raise QtfConfigException(error)
        if key not in self._parser[section]:
            error = f'Unknown key: "[{section}][{key}]"'
            raise QtfConfigException(error)
        value = self._parser[section][key]
        validator = self._validators[section][key][0]
        return validator.convert_from_ini(value)

    def set(self, section: str, key: str, value: Any) -> None:
        """ Convert the given key value to a string and set it in the config.

        Args:
            section (str): Section of the key.
            key (str): Key to get the value.
            value (Any): Value to set.

        Raises:
            QtfConfigException: If the section, key or value is invalid.
        """
        if not self._valid_config:
            error = 'No valid config loaded'
            raise QtfConfigException(error)
        if section not in self._parser:
            error = f'Unknown section: "[{section}]"'
            raise QtfConfigException(error)
        if key not in self._parser[section]:
            error = f'Unknown key: "[{section}][{key}]"'
            raise QtfConfigException(error)
        try:
            validator = self._validators[section][key][0]
            value_str = validator.convert_to_ini(value)
            self._parser[section][key] = value_str
        except QtfException as e:
            raise QtfConfigException(e)

    def _validate(self, accept_missing_keys: bool = False):
        """ Validate the config loaded.

        It checks:

        * If all sections and keys are presents.
        * Run for each key it's Validator's validate method.

        Args:
            accept_missing_keys (bool, optional): If set to True, the
                validation will accept missing keys and set them to their
                default value. Default to ``False``.

        Raises:
            QtfConfigException: If the config is not valid.
        """
        for section, keys in self._validators.items():
            if section not in self._parser:
                if accept_missing_keys:
                    self._parser[section] = {}
                else:
                    raise QtfConfigException(
                        f'Missing section "[{section}]"')

            for key, settings in keys.items():
                if key not in self._parser[section]:
                    if accept_missing_keys:
                        self._parser[section][key] = \
                            self._validators[section][key][1]
                    else:
                        raise QtfConfigException(
                            f'Missing key "[{section}][{key}]"')
                value = self._parser[section][key]

                try:
                    settings[0].validate_from_ini(value)
                except QtfException as e:
                    msg = f'Error in option "[{section}][{key}]": {e}'
                    raise QtfConfigException(msg)
