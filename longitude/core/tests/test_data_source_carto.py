from unittest import TestCase, mock

from longitude.core.common.config import EnvironmentConfiguration as Config
from carto.exceptions import CartoException

from ..data_sources.base import LongitudeRetriesExceeded
from ..data_sources.carto import CartoDataSource


class TestCartoDataSource(TestCase):

    def test_default_configuration_loads(self):
        with self.assertLogs(level='INFO') as log_test:
            Config.config = None  # To ensure that environment will be loaded
            carto_ds = CartoDataSource()
            module_name = 'longitude.core.common.config'
            self.assertEqual(log_test.output,
                             ['WARNING:%s:Empty environment configuration' % module_name,
                              "WARNING:%s:Using default value for root config" % module_name,
                              'INFO:%s:api_key key is using default value' % module_name,
                              'INFO:%s:api_version key is using default value' % module_name,
                              'INFO:%s:cache key is using default value' % module_name,
                              'INFO:%s:on_premise_domain key is using default value' % module_name,
                              'INFO:%s:user key is using default value' % module_name,
                              'INFO:%s:uses_batch key is using default value' % module_name]
                             )

            self.assertEqual('', carto_ds.get_config('api_key'))
            self.assertEqual('v2', carto_ds.get_config('api_version'))
            self.assertEqual('', carto_ds.get_config('on_premise_domain'))
            self.assertEqual('', carto_ds.get_config('user'))
            self.assertFalse(carto_ds.get_config('uses_batch'))

    @mock.patch.dict('longitude.core.common.config.os.environ', {})
    def test_setup_not_ready_if_empty_user(self):
        carto_ds = CartoDataSource('test_config')
        carto_ds.setup()
        self.assertFalse(carto_ds.is_ready)

    @mock.patch('longitude.core.common.config.EnvironmentConfiguration.get')
    def test_setup_needs_some_user(self, fake_config_get):
        fake_config_get.return_value = {
            'user': 'some_user'
        }
        carto_ds = CartoDataSource('test_config')
        carto_ds.setup()
        self.assertTrue(carto_ds.is_ready)
        self.assertEqual('https://some_user.carto.com', carto_ds.base_url)
        fake_config_get.assert_called_once_with('test_config', default={})

    @mock.patch('longitude.core.common.config.EnvironmentConfiguration.get')
    def test_setup_can_accept_on_premise_domain(self, fake_configuration_get):
        fake_configuration_get.return_value = {
            'user': 'some_on_premise_user',
            'on_premise_domain': 'some_cool_domain.io'
        }
        carto_ds = CartoDataSource('test_config')
        carto_ds.setup()
        self.assertTrue(carto_ds.is_ready)
        self.assertEqual('https://some_cool_domain.io/user/some_on_premise_user', carto_ds.base_url)
        fake_configuration_get.assert_called_once_with('test_config', default={})

    def test_succesful_query(self):
        ds = CartoDataSource()
        ds._sql_client = mock.MagicMock()
        ds._sql_client.send.return_value = {'rows': [], 'time': 42.0, 'fields': {}, 'total_rows': 0}
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
