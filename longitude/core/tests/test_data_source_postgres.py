from unittest import TestCase, mock

from longitude.core.common.config import EnvironmentConfiguration as Config
from ..data_sources.postgres.default import DefaultPostgresDataSource

TESTED_MODULE_PATH = 'longitude.core.data_sources.postgres.default.%s'


class TestSQLAlchemyDataSource(TestCase):
    def setUp(self):
        # We mock the calls to the internal engine creation for all tests
        # As we have a is_ready method, we just ensure that these calls return something
        patcher = mock.patch(TESTED_MODULE_PATH % 'psycopg2.connect')
        self.addCleanup(patcher.stop)
        self.connection_mock = patcher.start()

        # This will mock connection_mock, cursor and close methods in the psycopg
        self.connection_mock.return_value.cursor.return_value.close.return_value = None

    def test_default_configuration_loads(self):
        with self.assertLogs(level='INFO') as log_test:
            Config.config = None  # To ensure that environment will be loaded
            carto_ds = DefaultPostgresDataSource()
            module_name = 'longitude.core.common.config'
            self.assertEqual(
                ['WARNING:%s:Empty environment configuration' % module_name,
                 'WARNING:%s:Using default value for root config' % module_name,
                 'INFO:%s:db key is using default value' % module_name,
                 'INFO:%s:host key is using default value' % module_name,
                 'INFO:%s:password key is using default value' % module_name,
                 'INFO:%s:port key is using default value' % module_name,
                 'INFO:%s:user key is using default value' % module_name
                 ], log_test.output
            )

            self.assertEqual('', carto_ds.get_config('db'))
            self.assertEqual('localhost', carto_ds.get_config('host'))
            self.assertEqual('', carto_ds.get_config('password'))
            self.assertEqual(5432, carto_ds.get_config('port'))
            self.assertEqual('postgres', carto_ds.get_config('user'))

            self.assertTrue(carto_ds.is_ready)

    def test_query_without_commit(self):
        fake_fields = ['field_A', 'field_B']
        fake_rows = [[], []]

        self.connection_mock.return_value.cursor.return_value.execute.return_value = None
        self.connection_mock.return_value.cursor.return_value.description = fake_fields
        self.connection_mock.return_value.cursor.return_value.fetchall.return_value = fake_rows

        carto_ds = DefaultPostgresDataSource()
        data = carto_ds.execute_query(query_template="some valid query", params={}, needs_commit=False,
                                      query_config=None)

        # Queries with no commit return an dictionary with, at least, fields and rows
        self.assertTrue('fields' in data)
        self.assertTrue('rows' in data)
        self.assertTrue('profiling' in data)

        self.assertCountEqual(fake_fields, data['fields'])
        self.assertCountEqual(fake_rows, data['rows'])

    def test_query_with_commit(self):
        self.connection_mock.return_value.commit().return_value = None
        self.connection_mock.return_value.cursor.return_value.execute.return_value = None

        carto_ds = DefaultPostgresDataSource()
        data = carto_ds.execute_query(query_template="some valid query", params={}, needs_commit=True,
                                      query_config=None)

        # Queries with no commit return an dictionary with, at least, fields and rows
        self.assertTrue('fields' in data)
        self.assertTrue('rows' in data)
        self.assertTrue('profiling' in data)

        self.assertCountEqual([], data['fields'])
        self.assertCountEqual([], data['rows'])

        self.assertTrue('commit_time' in data['profiling'])
