from unittest import TestCase

from src.core.common.config import LongitudeConfigurable
from src.core.common.exceptions import LongitudeConfigError


class TestConfig(TestCase):
    def test_config(self):
        # Config must be a dictionary
        with self.assertRaises(TypeError):
            LongitudeConfigurable(config=[])
        with self.assertRaises(TypeError):
            LongitudeConfigurable(config="")
        with self.assertRaises(TypeError):
            LongitudeConfigurable(config=0)

        # Any values can go in the configuration dictionary but not expected ones trigger a warning
        config = {"some_config_value": 0, "some_another_config_value": "tomato"}
        with self.assertLogs(level='WARNING') as log_test:
            ds = LongitudeConfigurable(config)
            self.assertEqual(log_test.output,
                             [
                                 'WARNING:src.core.common.config:some_another_config_value is an unexpected config value',
                                 'WARNING:src.core.common.config:some_config_value is an unexpected config value'])

        # Values in the config can be retrieved using get_config. If no default or config is defined, None is returned.
        ds._default_config['some_config_value'] = 42
        ds._default_config['some_none_value'] = None
        self.assertEqual(0, ds.get_config('some_config_value'))
        self.assertEqual(None, ds.get_config('some_none_value'))

        # We do not allow trying to get a config value out of the default keys
        with self.assertRaises(LongitudeConfigError):
            self.assertIsNone(ds.get_config('some_random_value_that_does_not_exist_in_config_or_defaults'))
