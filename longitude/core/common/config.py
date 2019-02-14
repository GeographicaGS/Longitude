import logging
import os

from .exceptions import LongitudeConfigError


class EnvironmentConfiguration:
    prefix = 'LONGITUDE'
    separator = '__'
    config = None
    logger = logging.getLogger(__name__)

    @classmethod
    def _load_environment_variables(cls):
        """
        It loads environment variables into the internal dictionary.

        Load is done by grouping and nesting environment variables following this convention:
        1. Only variables starting with the prefix are taken (i.e. LONGITUDE)
        2. For each separator used, a new nested object is created inside its parent (i.e. SEPARATOR is '__')
        3. The prefix indicates the root object (i.e. LONGITUDE__ is the default root dictionary)

        :return: None
        """
        cls.config = {}
        for v in [k for k in os.environ.keys() if k.startswith(cls.prefix)]:
            value_path = v.split(cls.separator)[1:]
            cls._append_value(os.environ.get(v), value_path, cls.config)
        if cls.config == {}:
            cls.logger.warning('Empty environment configuration')

    @classmethod
    def get(cls, key=None, default=None):
        """
        Returns a nested config value from the configuration. It allows getting values as a series of joined keys using
        dot ('.') as separator. This will search for keys in nested dictionaries until a final value is found.

        :param key: String in the form of 'parent.child.value...'. It must replicate the configuration nested structure.
        :param default: Returned value if nested key is not found
        :return: It returns an integer, a string or a nested dictionary. If none of these is found, it returns None.
        """

        # We do a lazy load in the first access
        if cls.config is None:
            cls._load_environment_variables()

        if key is not None:
            value = cls._get_nested_key(key, cls.config)
            if value:
                if isinstance(value, str) and value.lower() in ['true', 'false', 'yes', 'no', 'y', 'n']:
                    value = value.lower() in ['true', 'yes', 'y']
                if default is not None:
                    cast_type = type(default)
                    value = cast_type(value)
                return value
            else:
                if default is not None:
                    if key:
                        cls.logger.warning('Using default value for config key %s' % key)
                    else:
                        cls.logger.warning('Using default value for root config')
                else:
                    cls.logger.warning('Config key %s not found and no default has been defined.' % key)
                return default
        else:
            return cls.config

    @staticmethod
    def _get_nested_key(key, d):
        """

        :param key:
        :param d:
        :return:
        """
        key_path = key.split('.')
        root_key = key_path[0].lower()

        if root_key in d.keys():
            if len(key_path) == 1:
                return d[root_key]  # If a single node is in the path, it is the final one
            # If there are more than one nodes left, keep digging...
            return EnvironmentConfiguration._get_nested_key('.'.join(key_path[1:]), d[root_key])
        else:
            return None  # Nested key was not found in the config

    @staticmethod
    def _append_value(value, value_path, d):
        root_path = value_path[0].lower()
        if len(value_path) == 1:
            d[root_path] = value
        else:
            if root_path not in d.keys():
                d[root_path] = {}
            EnvironmentConfiguration._append_value(value, value_path[1:], d[root_path])


class LongitudeConfigurable:
    """
    Any subclass will have a nice get_config(key) method to retrieve configuration values
    """
    _default_config = {}
    _config = {}

    def __init__(self, config=''):
        if isinstance(config, str):
            self.name = config
            self._config = EnvironmentConfiguration.get(config, default={})
        else:
            self.name = ''
            self._config = config

        self.logger = logging.getLogger(__class__.__module__)
        default_keys = set(self._default_config.keys())
        config_keys = set(self._config.keys()) if self._config is not None else set([])
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
            raise LongitudeConfigError("%s is not a valid config value. Check your defaults as reference." % key)
        try:
            return self._config[key]
        except (TypeError, KeyError):
            return self._default_config[key]
