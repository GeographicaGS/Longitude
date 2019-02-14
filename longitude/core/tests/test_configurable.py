from unittest import TestCase, mock

from longitude.core.common.config import LongitudeConfigurable
from longitude.core.common.exceptions import LongitudeConfigError


@mock.patch('longitude.core.common.config.EnvironmentConfiguration.get')
class TestConfig(TestCase):

    def test_config(self, fake_get_config):
        # Any values can go in the configuration dictionary but not expected ones trigger a warning
        fake_get_config.return_value = {"some_config_value": 0, "some_another_config_value": "tomato"}

        with self.assertLogs(level='WARNING') as log_test:
            ds = LongitudeConfigurable(config='test_config')
            self.assertEqual(log_test.output,
                             [
                                 'WARNING:longitude.core.common.config:some_another_config_value is an unexpected config value',
                                 'WARNING:longitude.core.common.config:some_config_value is an unexpected config value'])

        # Values in the config can be retrieved using get_config. If no default or config is defined, None is returned.
        ds._default_config['some_config_value'] = 42
        ds._default_config['some_none_value'] = None
        self.assertEqual(0, ds.get_config('some_config_value'))
        self.assertEqual(None, ds.get_config('some_none_value'))

        fake_get_config.assert_called_once_with('test_config', default={})

        # We do not allow trying to get a config value out of the default keys
        with self.assertRaises(LongitudeConfigError):
            self.assertIsNone(ds.get_config('some_random_value_that_does_not_exist_in_config_or_defaults'))

    def test_get_config_root(self, fake_get_config):
        class SomeConfigurableClass(LongitudeConfigurable):
            _default_config = {
                'a': None,
                'b': 'this will not be overwritten'
            }

        fake_get_config.return_value = {
            'a': 'custom_value'
        }
        ds = SomeConfigurableClass(config='test_config')
        c = ds.get_config()
        expected_config = {
            'a': 'custom_value',
            'b': 'this will not be overwritten'
        }
        self.assertEqual(expected_config, c)
        fake_get_config.assert_called_once_with('test_config', default={})
