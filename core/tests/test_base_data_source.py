from unittest import TestCase
from core.data_sources.base import DataSource, DataSourceQueryConfig, LongitudeQueryResponse


class TestLongitudeQueryResponse(TestCase):
    def test_preview(self):
        qr = LongitudeQueryResponse(
            rows=[['A' + str(v), 'B' + str(v)] for v in range(20)],
            fields={'As': {'type': 'string'}, 'Bs': {'type': 'string'}},
            profiling={'response_time': 42.0}
        )

        render_top = qr.preview_top()
        expected_render_top = \
"""| As	| Bs		|
| A0	| B0		|
| A1	| B1		|
| A2	| B2		|
| A3	| B3		|
| A4	| B4		|
| A5	| B5		|
| A6	| B6		|
| A7	| B7		|
| A8	| B8		|
| A9	| B9		|

... time = 42.000000"""
        self.assertEqual(expected_render_top, render_top)

        render_bottom = qr.preview_bottom()
        expected_render_bottom = \
"""| As	| Bs		|
| A10	| B10		|
| A11	| B11		|
| A12	| B12		|
| A13	| B13		|
| A14	| B14		|
| A15	| B15		|
| A16	| B16		|
| A17	| B17		|
| A18	| B18		|
| A19	| B19		|

... time = 42.000000"""
        self.assertEqual(expected_render_bottom, render_bottom)


class TestDataSourceQueryConfig(TestCase):
    def test_copy(self):
        a = DataSourceQueryConfig()
        b = a.copy()

        self.assertNotEqual(a, b)
        self.assertEqual(a.__dict__, b.__dict__)


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

    def test_abstract_methods_are_not_implemented(self):
        ds = DataSource({})
        with self.assertRaises(NotImplementedError):
            ds.is_ready
        with self.assertRaises(NotImplementedError):
            ds.query(statement='whatever')

    def test_copy_default_query_config(self):
        ds = DataSource({})
        the_copy = ds.copy_default_query_config()
        self.assertNotEqual(the_copy, ds._default_query_config)
        self.assertEqual(the_copy.__dict__, ds._default_query_config.__dict__)
