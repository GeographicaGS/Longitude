import logging
import os

from .exceptions import LongitudeConfigError


class EnvironmentConfiguration:

    def __init__(self, d):
        self._original_config = d
        self._parsed_config = dict(d)

        self._parse_env_vars_references(self._parsed_config)

    def __getitem__(self, key):
        return self._parsed_config[key]

    @staticmethod
    def _parse_env_vars_references(dictionary):
        """
        Modifies a dictionary like this:
          * Recursively
          * If a value is a string starting with '=', it gets substituted by the corresponding environment variable
        :param dictionary: Dictionary that will be modified.
        :return: Nothing
        """

        for k in dictionary.keys():
            if isinstance(dictionary[k], dict):
                EnvironmentConfiguration._parse_env_vars_references(dictionary[k])
            elif isinstance(dictionary[k], str) and dictionary[k].startswith('='):
                env_var = dictionary[k][1:]  # We remove the '='
                value = os.environ.get(env_var)
                if value:
                    dictionary[k] = value
                else:
                    dictionary[k] += ' [NOT FOUND]'


class LongitudeConfigurable:
    """
    Any subclass will have a nice get_config(key) method to retrieve configuration values
    """
    _default_config = {}
    _config = {}

    def __init__(self, config=None):
        if config is not None and not isinstance(config, dict):
            raise TypeError('Config object must be a dictionary')

        self._config = config or {}
        self.logger = logging.getLogger(__class__.__module__)
        default_keys = set(self._default_config.keys())
        config_keys = set(config.keys()) if config is not None else set([])
        unexpected_config_keys = list(config_keys.difference(default_keys))
        using_defaults_for = list(default_keys.difference(config_keys))

        unexpected_config_keys.sort()
        using_defaults_for.sort()

        for k in unexpected_config_keys:
            self.logger.warning("%s is an unexpected config value" % k)

        for k in using_defaults_for:
            self.logger.info("%s key is using default value" % k)

    def get_config(self, key=None):
        """
         Getter for configuration values
         :param key: Key in the configuration dictionary. If no key is provided, the full config is returned.
         :return: Current value of the chosen key
         """
        if key is None:
            config_template = dict(self._default_config)
            config_template.update(self._config)
            return config_template

        if key not in self._default_config.keys():
            raise LongitudeConfigError("%s is not a valid config value. Check your defaults as reference.")
        try:
            return self._config[key]
        except (TypeError, KeyError):
            return self._default_config[key]
