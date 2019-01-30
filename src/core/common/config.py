import logging

from .exceptions import LongitudeConfigError


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

    def get_config(self, key):
        """
         Getter for configuration values
         :param key: Key in the configuration dictionary
         :return: Current value of the chosen key
         """

        if key not in self._default_config.keys():
            raise LongitudeConfigError("%s is not a valid config value. Check your defaults as reference.")
        try:
            return self._config[key]
        except (TypeError, KeyError):
            try:
                return self._default_config[key]
            except KeyError:
                return None
