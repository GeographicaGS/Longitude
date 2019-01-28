from unittest import TestCase, mock

from carto.exceptions import CartoException

from ..data_sources.base import LongitudeRetriesExceeded
from ..data_sources.carto import CartoDataSource


class TestCartoDataSource(TestCase):

    def test_default_configuration_loads(self):
        with self.assertLogs(level='INFO') as log_test:
            carto_ds = CartoDataSource()
            self.assertEqual(log_test.output,
                             ['INFO:src.core.data_sources.carto:api_key key is using default value',
                              'INFO:src.core.data_sources.carto:api_version key is using default value',
                              'INFO:src.core.data_sources.carto:cache key is using default value',
                              'INFO:src.core.data_sources.carto:on_premise_domain key is using default value',
                              'INFO:src.core.data_sources.carto:user key is using default value',
                              'INFO:src.core.data_sources.carto:uses_batch key is using default value']
                             )

            self.assertEqual('', carto_ds.get_config('api_key'))
            self.assertEqual('v2', carto_ds.get_config('api_version'))
            self.assertEqual('', carto_ds.get_config('on_premise_domain'))
            self.assertEqual('', carto_ds.get_config('user'))
            self.assertFalse(carto_ds.get_config('uses_batch'))

    def test_setup_not_ready_if_empty_user(self):
        carto_ds = CartoDataSource({
            'uses_batch': True  # Just to enable that coverage branch for now
        })
        carto_ds.setup()
        self.assertFalse(carto_ds.is_ready)

    def test_setup_needs_some_user(self):
        carto_ds = CartoDataSource({
            'user': 'some_user'
        })
        carto_ds.setup()
        self.assertTrue(carto_ds.is_ready)
        self.assertEqual('https://some_user.carto.com', carto_ds.base_url)

    def test_setup_can_accept_on_premise_domain(self):
        carto_ds = CartoDataSource({
            'user': 'some_on_premise_user',
            'on_premise_domain': 'some_cool_domain.io'
        })
        carto_ds.setup()
        self.assertTrue(carto_ds.is_ready)
        self.assertEqual('https://some_cool_domain.io/user/some_on_premise_user', carto_ds.base_url)

    def test_succesful_query(self):
        ds = CartoDataSource()
        ds._sql_client = mock.MagicMock()
        ds._sql_client.send.return_value = {'rows': [], 'time': 42.0, 'fields': {}}
        result = ds.query('some query')
        ds._sql_client.send.assert_called_with('some query', do_post=False, format='json', parse_json=True)
        self.assertEqual([], result.rows)
        self.assertEqual(42, result.profiling['response_time'])

    def test_wrong_query(self):
        ds = CartoDataSource()
        ds._sql_client = mock.MagicMock()
        ds._sql_client.send.side_effect = CartoException
        with self.assertRaises(LongitudeRetriesExceeded):
            ds.query('some irrelevant query')
