from sqlalchemy import create_engine
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.ext.declarative import declarative_base

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
        return self._connection.execute(query_template, params)

    def parse_response(self, response):

        try:
            raw_result = response.fetchall()
            response.close()
        except ResourceClosedError:
            raw_result = None

        return raw_result
