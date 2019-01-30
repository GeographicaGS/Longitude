import psycopg2
import psycopg2.extensions
from ..base import DataSource
from ..base import LongitudeQueryResponse


class DefaultPostgresDataSource(DataSource):
    _default_config = {
        'host': 'localhost',
        'port': 5432,
        'db': '',
        'user': 'postgres',
        'password': ''
    }

    def __init__(self, config=None, cache_class=None):
        self._conn = None
        self._cursor = None
        super().__init__(config, cache_class=cache_class)

    def __del__(self):
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()

    def setup(self):
        self._conn = psycopg2.connect(
            host=self.get_config('host'),
            port=self.get_config('port'),
            database=self.get_config('db'),
            user=self.get_config('user'),
            password=self.get_config('password')
        )

        self._cursor = self._conn.cursor()
        super().setup()

    def is_ready(self):
        return super().is_ready and self._conn and self._cursor

    def execute_query(self, formatted_query, query_config, **opts):
        self._cursor.execute(formatted_query)
        data = None
        if self._cursor.description:
            data = {
                'fields': self._cursor.description,
                'rows': self._cursor.fetchall()
            }
        self._conn.commit()
        return data

    @staticmethod
    def _type_as_string(type_id):
        return psycopg2.extensions.string_types[type_id]

    def parse_response(self, response):
        if response:
            fields_names = {n.name: self._type_as_string(n.type_code).name for n in response['fields']}
            return LongitudeQueryResponse(rows=response['rows'], fields=fields_names)
        return None
