from time import time

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from .common import psycopg2_type_as_string
from src.core.common.query_response import LongitudeQueryResponse
from src.core.data_sources.base import DataSource


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

    def __init__(self, config=None, cache_class=None):
        # https://docs.sqlalchemy.org/en/latest/dialects/postgresql.html

        self._engine = None
        self._connection = None

        super().__init__(config, cache_class=cache_class)

    def __del__(self):
        if self._connection:
            self._connection.close()

    def setup(self):
        connection_string_template = 'postgresql://%(user)s:%(password)s@%(host)s:%(port)d/%(db)s'
        self._engine = create_engine(connection_string_template % self.get_config(), echo=True)
        self._connection = self._engine.connect()

        super().setup()

    @property
    def is_ready(self):
        return self._engine is not None and self._connection is not None

    def execute_query(self, query_template, params, needs_commit, query_config, **opts):
        data = {
            'fields': [],
            'rows': [],
            'profiling': {}
        }

        start = time()
        response = self._connection.execute(query_template, params)
        data['profiling']['execute_time'] = time() - start

        if response.returns_rows:
            data['fields'] = response.cursor.description
            data['rows'] = response.fetchall()

        # TODO: Check auto-commit feature. How do we want to implement this here?

        return data

    def parse_response(self, response):

        if response:
            raw_fields = response['fields']
            fields_names = {n.name: {'type': psycopg2_type_as_string(n.type_code).name} for n in raw_fields}
            rows = [{raw_fields[i].name: f for i, f in enumerate(row_data)} for row_data in response['rows']]
            return LongitudeQueryResponse(rows=rows, fields=fields_names, profiling=response['profiling'])
        return None
