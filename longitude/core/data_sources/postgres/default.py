from time import time

import psycopg2
import psycopg2.extensions

from ...common.query_response import LongitudeQueryResponse
from ..base import DataSource
from .common import psycopg2_type_as_string


class DefaultPostgresDataSource(DataSource):
    _default_config = {
        'host': 'localhost',
        'port': 5432,
        'db': '',
        'user': 'postgres',
        'password': ''
    }

    def __init__(self, config='', cache_class=None, cache=None):
        super().__init__(config=config, cache_class=cache_class, cache=cache)
        self._conn = psycopg2.connect(
            host=self.get_config('host'),
            port=self.get_config('port'),
            database=self.get_config('db'),
            user=self.get_config('user'),
            password=self.get_config('password')
        )

        self._cursor = self._conn.cursor()

    def __del__(self):
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()

    def is_ready(self):
        return super().is_ready and self._conn and self._cursor

    def execute_query(self, query_template, params, needs_commit, query_config, **opts):
        data = {
            'fields': [],
            'rows': [],
            'profiling': {}
        }

        start = time()
        self._cursor.execute(query_template, params)
        data['profiling']['execute_time'] = time() - start

        if self._cursor.description:
            data['fields'] = self._cursor.description
            data['rows'] = self._cursor.fetchall()

        if needs_commit:
            start = time()
            self._conn.commit()
            data['profiling']['commit_time'] = time() - start

        return data

    def parse_response(self, response):
        if response:
            raw_fields = response['fields']
            fields_names = {n.name: {'type': psycopg2_type_as_string(n.type_code).name} for n in raw_fields}
            rows = [{raw_fields[i].name: f for i, f in enumerate(row_data)} for row_data in response['rows']]
            return LongitudeQueryResponse(rows=rows, fields=fields_names, profiling=response['profiling'])
        return None

    def copy_from(self, data, filepath, to_table):
        headers = data.readline().decode('utf-8').split(',')
        self._cursor.copy_from(data, to_table, columns=headers, sep=',')
        self._conn.commit()

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
