from unittest import TestCase, mock
from carto.exceptions import CartoException
from core.data_sources.carto import CartoDataSource


class TestCartoDataSource(TestCase):

    def test_default_configuration_loads(self):
        with self.assertLogs(level='INFO') as log_test:
            carto_ds = CartoDataSource()
            self.assertEqual(log_test.output,
                             ['INFO:core.data_sources.carto:api_key key is using default value',
                              'INFO:core.data_sources.carto:api_version key is using default value',
                              'INFO:core.data_sources.carto:user_url key is using default value',
                              'INFO:core.data_sources.carto:uses_batch key is using default value']
                             )

            self.assertEqual('', carto_ds.get_config('api_key'))
            self.assertEqual('v2', carto_ds.get_config('api_version'))
            self.assertEqual('', carto_ds.get_config('user_url'))
            self.assertFalse(carto_ds.get_config('uses_batch'))

    def test_setup_fails_with_default_config(self):
        import warnings
        # Default config MUST NOT BE USABLE for authentication
        with warnings.catch_warnings(record=True) as w:
            with self.assertRaises(CartoException) as error:
                CartoDataSource().setup()
            self.assertEqual(1, len(w), 'Carto will warn us about not using https')

    def test_setup_needs_a_valid_user_url(self):
        config = {
            'user_url': 'https://fake_user.carto.com',
            'uses_batch': True

        }
        carto_ds = CartoDataSource(config=config)
        carto_ds.setup()
        self.assertTrue(carto_ds.is_ready)
