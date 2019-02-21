from unittest import TestCase, mock

from longitude.core.common.config import EnvironmentConfiguration as Config
from longitude.core.common.query_response import LongitudeQueryResponse
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
            postgres_ds = DefaultPostgresDataSource()
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

            self.assertEqual('', postgres_ds.get_config('db'))
            self.assertEqual('localhost', postgres_ds.get_config('host'))
            self.assertEqual('', postgres_ds.get_config('password'))
            self.assertEqual(5432, postgres_ds.get_config('port'))
            self.assertEqual('postgres', postgres_ds.get_config('user'))

            self.assertTrue(postgres_ds.is_ready)

    def test_query_without_commit(self):
        fake_fields = ['field_A', 'field_B']
        fake_rows = [[], []]

        self.connection_mock.return_value.cursor.return_value.execute.return_value = None
        self.connection_mock.return_value.cursor.return_value.description = fake_fields
        self.connection_mock.return_value.cursor.return_value.fetchall.return_value = fake_rows

        postgres_ds = DefaultPostgresDataSource()
        data = postgres_ds.execute_query(query_template="some valid query", params={}, needs_commit=False,
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

        postgres_ds = DefaultPostgresDataSource()
        data = postgres_ds.execute_query(query_template="some valid query", params={}, needs_commit=True,
                                         query_config=None)

        # Queries with no commit return an dictionary with, at least, fields and rows
        self.assertTrue('fields' in data)
        self.assertTrue('rows' in data)
        self.assertTrue('profiling' in data)

        self.assertCountEqual([], data['fields'])
        self.assertCountEqual([], data['rows'])

        self.assertTrue('commit_time' in data['profiling'])

    def test_parse_response(self):
        class FakeField:
            def __init__(self, name, type_code):
                self.name = name
                self.type_code = type_code

        postgres_ds = DefaultPostgresDataSource()
        self.assertIsNone(postgres_ds.parse_response())

        response = {
            'fields': [FakeField('field_A', 23), FakeField('field_B', 19)],
            'rows': [
                [666, 'day of the beast'],
                [42, 'the answer'],
                [69, 'idk'],
                [-1, 'nope']
            ],
            'profiling': {'metric_A': 42, 'metric_B': 'big'}
        }

        parsed_response = postgres_ds.parse_response(response)
        self.assertTrue(isinstance(parsed_response, LongitudeQueryResponse))

        self.assertEqual(4, len(parsed_response.rows))
        self.assertEqual('INTEGER', parsed_response.fields['field_A']['type'])  # This is the 23 above
        self.assertEqual('STRING', parsed_response.fields['field_B']['type'])  # This is the 19 above
        self.assertFalse(parsed_response.from_cache)
        self.assertEqual(response['profiling'], parsed_response.profiling)
