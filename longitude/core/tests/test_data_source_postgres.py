from unittest import TestCase, mock

from ..data_sources.postgres.default import PostgresDataSource

TESTED_MODULE_PATH = 'longitude.core.data_sources.postgres.default.%s'


class TestSQLAlchemyDataSource(TestCase):
    def setUp(self):
        # We mock the calls to the internal engine creation for all tests
        patcher = mock.patch(TESTED_MODULE_PATH % 'psycopg2.connect')
        self.addCleanup(patcher.stop)
        self.connection_mock = patcher.start()

        # This will mock connection_mock, cursor and close methods in the psycopg
        self.connection_mock.return_value.cursor.return_value.close.return_value = None

    def test_query_without_commit(self):
        fake_fields = ['field_A', 'field_B']
        fake_rows = [[], []]

        self.connection_mock.return_value.cursor.return_value.execute.return_value = None
        self.connection_mock.return_value.cursor.return_value.description = fake_fields
        self.connection_mock.return_value.cursor.return_value.fetchall.return_value = fake_rows

        carto_ds = PostgresDataSource()
        data = carto_ds.execute_query(
            query_template="some valid query",
            params={},
            needs_commit=False,
            query_config=None
        )

        # Queries with no commit return an dictionary with, at least, fields and rows
        self.assertTrue('fields' in data)
        self.assertTrue('rows' in data)

        self.assertCountEqual(fake_fields, data['fields'])
        self.assertCountEqual(fake_rows, data['rows'])

    def test_query_with_commit(self):
        self.connection_mock.return_value.commit().return_value = None
        self.connection_mock.return_value.cursor.return_value.execute.return_value = None

        carto_ds = PostgresDataSource()
        data = carto_ds.execute_query(
            query_template="some valid query",
            params={},
            needs_commit=True,
            query_config=None
        )

        # Queries with no commit return an dictionary with, at least, fields and rows
        self.assertTrue('fields' in data)
        self.assertTrue('rows' in data)

        self.assertCountEqual([], data['fields'])
        self.assertCountEqual([], data['rows'])
