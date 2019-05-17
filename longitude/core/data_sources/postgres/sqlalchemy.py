from pandas import read_sql_table, read_sql_query

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from longitude.core.common.query_response import LongitudeQueryResponse
from longitude.core.data_sources.base import DataSource

from .common import psycopg2_type_as_string


class SQLAlchemyDataSource(DataSource):
    _default_config = {
        'host': 'localhost',
        'port': 5432,
        'db': '',
        'user': 'postgres',
        'password': ''
    }

    _Base = None

    @property
    def base_class(self):
        if self._Base is None:
            self._Base = declarative_base()
        return self._Base

    def create_all(self):
        self.base_class.metadata.create_all(self._engine)

    def __init__(self, options={}):
        # https://docs.sqlalchemy.org/en/latest/dialects/postgresql.html

        super().__init__(options)

        self.options = {
            'host': options.get('host', 'localhost'),
            'port': options.get('port', 5432),
            'db': options.get('db', ''),
            'user': options.get('user', 'postgres'),
            'password': options.get('password', '')
        }
        self._auto_commit = options.get('auto_commit', False)

        connection_string_template = 'postgresql://%(user)s:%(password)s@%(host)s:%(port)d/%(db)s'
        self._engine = create_engine(connection_string_template % self.options, echo=True)
        self._connection = self._engine.connect()

    def __del__(self):
        if self._connection:
            self._connection.close()

    def execute_query(self, query_template, params, **opts):
        data = {
            'fields': [],
            'rows': []
        }

        response = self._connection.execute(query_template, params)

        if response.returns_rows:
            data['fields'] = response.cursor.description
            data['rows'] = response.fetchall()

        # TODO: Check auto-commit feature. How do we want to implement this here?

        return data

    def commit(self):
        self._connection.commit()

    def parse_response(self, response):
        if response:
            raw_fields = response['fields']
            fields_names = {n.name: {'type': psycopg2_type_as_string(n.type_code)} for n in raw_fields}
            rows = [dict(zip(fields_names.keys(), row)) for row in response['rows']]
            return LongitudeQueryResponse(rows=rows, fields=fields_names)
        return None

    def copy_from(self, data, filepath, to_table):
        headers = data.readline().decode('utf-8').split(',')
        conn = self._engine.raw_connection()
        conn.cursor().copy_from(data, to_table, columns=headers, sep=',')
        if self._auto_commit:
            self.commit()

    def read_dataframe(self, table_name='', *args, **kwargs):
        return read_sql_table(table_name=table_name, con=self._engine)

    def query_dataframe(self, query='', *args, **kwargs):
        return read_sql_query(sql=query, con=self._engine, *args, **kwargs)

    def write_dataframe(self, df, table_name='', *args, **kwargs):
        return df.to_sql(name=table_name, con=self._engine, *args, **kwargs)
