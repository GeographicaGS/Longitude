import psycopg2
import psycopg2.extensions

from ...common.query_response import LongitudeQueryResponse
from ..base import DataSource
from .common import psycopg2_type_as_string


class PostgresDataSource(DataSource):

    def __init__(self, options={}):
        super().__init__(options)
        self._conn = psycopg2.connect(
            host=options.get('host', 'localhost'),
            port=options.get('port', 5432),
            database=options.get('db', ''),
            user=options.get('user', 'postgres'),
            password=options.get('password', '')
        )
        self._auto_commit = options.get('auto_commit', False)

        self._cursor = self._conn.cursor()

    def __del__(self):
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()

    def execute_query(self, query_template, params, **opts):
        data = {
            'fields': [],
            'rows': []
        }

        self._cursor.execute(query_template, params)

        if self._cursor.description:
            data['fields'] = self._cursor.description
            data['rows'] = self._cursor.fetchall()

        if self._auto_commit:
            self.commit()

        return data

    def commit(self):
        self._conn.commit()

    def parse_response(self, response):
        if response:
            raw_fields = response['fields']
            fields_names = {n.name: {'type': psycopg2_type_as_string(n.type_code)} for n in raw_fields}
            rows = [dict(zip(fields_names.keys(), row)) for row in response['rows']]
            return LongitudeQueryResponse(rows=rows, fields=fields_names)
        return None

    def copy_from(self, data, filepath, to_table):
        headers = data.readline().decode('utf-8').split(',')
        self._cursor.copy_from(data, to_table, columns=headers, sep=',')
        if self._auto_commit:
            self.commit()

    def write_dataframe(self, *args, **kwargs):
        raise NotImplementedError('Use the SQLAlchemy data source if you need dataframes!')

    def read_dataframe(self, *args, **kwargs):
        # TODO: It is possible to read dataframes using psycopg2, but we do not support it for now to encourage
        #  the use of SQLAlchemy for such tasks
        raise NotImplementedError('Use the SQLAlchemy data source if you need dataframes!')

    def query_dataframe(self, *args, **kwargs):
        # TODO: It is possible to read dataframes using psycopg2, but we do not support it for now to encourage
        #  the use of SQLAlchemy for such tasks
        raise NotImplementedError('Use the SQLAlchemy data source if you need dataframes!')
