import psycopg2
from ..base import DataSource


class DefaultPostgresDataSource(DataSource):
    default_config = {
        'user': 'postgres',
        'password': '',
        'domain': 'localhost',
        'port': 5432

    }

    def __init__(self, config=None, cache_class=None):
        super().__init__(config, cache_class=cache_class)

    def setup(self):
        super().setup()

    def is_ready(self):
        return super().is_ready

    def execute_query(self, formatted_query, query_config, **opts):
        pass

    def parse_response(self, response):
        pass
