import logging


class DataSource:
    logger = logging.getLogger(__name__)
    default_config = {}

    def __init__(self, config=None):
        if config is None:
            config = {}

        if not isinstance(config, dict):
            raise TypeError('Config object must be a dictionary')

        default_keys = set(self.default_config.keys())
        config_keys = set(config.keys())
        unexpected_config_keys = list(config_keys.difference(default_keys))
        using_defaults_for = list(default_keys.difference(config_keys))

        unexpected_config_keys.sort()
        using_defaults_for.sort()

        for k in unexpected_config_keys:
            self.logger.warning("%s is an unexpected config value" % k)

        for k in using_defaults_for:
            self.logger.info("%s key is using default value" % k)

        self._config = config

    @property
    def is_ready(self):
        return NotImplementedError

    def query(self, params):
        raise NotImplementedError

    def get_config(self, key):
        try:
            return self._config[key]
        except KeyError:
            try:
                return self.default_config[key]
            except KeyError:
                return None
