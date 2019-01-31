from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.data_sources.base import DataSource


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
        self._session = None

        super().__init__(config, cache_class=cache_class)

    def setup(self):
        connection_string_template = 'postgresql://%(user)s:%(password)s@%(host)s:%(port)d/%(db)s'
        self._engine = create_engine(connection_string_template % self.get_config(), echo=True)
        self._session = sessionmaker(bind=self._engine)

        super().setup()

    @property
    def is_ready(self):
        # TODO: Write how, after setup, you can know if queries can be executed (return True) or not (return False)
        return self._engine is not None and self._session is not None

    def execute_query(self, query_template, params, needs_commit, query_config, **opts):
        # TODO: Write how the database query is executed and return the response or None
        pass

    def parse_response(self, response):
        # TODO: Write how the database query response is converted into a LongitudeQueryResponse object
        pass
