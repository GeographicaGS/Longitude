from unittest import TestCase
from core.data_sources.base import DataSource


class TestDataSource(TestCase):
    def test_config(self):

        # Config must be a dictionary
        with self.assertRaises(TypeError):
            DataSource([])
        with self.assertRaises(TypeError):
            DataSource("")
        with self.assertRaises(TypeError):
            DataSource(0)

        # Any values can go in the configuration dictionary but not expected ones trigger a warning
        config = {"some_config_value": 0, "some_another_config_value": "tomato"}
        with self.assertLogs(level='WARNING') as log_test:
            ds = DataSource(config)
            self.assertEqual(log_test.output,
                             ['WARNING:core.data_sources.base:some_another_config_value is an unexpected config value',
                              'WARNING:core.data_sources.base:some_config_value is an unexpected config value'])

        # Values in the config can be retrieved using get_config. If no default or config is defined, None is returned.
        self.assertEqual(0, ds.get_config('some_config_value'))
        self.assertEqual("tomato", ds.get_config('some_another_config_value'))
        self.assertIsNone(ds.get_config('some_random_value_that_does_not_exist_in_config_or_defaults'))

    def test_query_is_custom(self):
        ds = DataSource({})
        with self.assertRaises(NotImplementedError):
            ds.query(statement='whatever')
