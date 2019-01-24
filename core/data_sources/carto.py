from carto.exceptions import CartoException

from core.data_sources.base import DataSource, LongitudeQueryCannotBeExecutedException
from carto.auth import APIKeyAuthClient
from carto.sql import BatchSQLClient, SQLClient


class CartoDataSource(DataSource):
    default_config = {
        'api_version': 'v2',
        'uses_batch': False,
        'api_key': '',
        'user_url': ''
    }

    def __init__(self, config=None):
        super().__init__(config)
        self._sql_client = None
        self._batch_client = None
        self.set_custom_query_default('do_post', False)
        self.set_custom_query_default('parse_json', True)
        self.set_custom_query_default('format', 'json')

    def setup(self):
        auth_client = APIKeyAuthClient(api_key=self.get_config('api_key'), base_url=self.get_config('user_url'))
        self._sql_client = SQLClient(auth_client, api_version=self.get_config('api_version'))

        if self.get_config('uses_batch'):
            self._batch_client = BatchSQLClient(auth_client)

    @property
    def is_ready(self):
        sql_setup_ready = self._sql_client is not None
        batch_setup_ready = not self.get_config('uses_batch') or (self._batch_client is not None)
        return sql_setup_ready and batch_setup_ready

    def execute_query(self, formatted_statement, query_config, **opts):
        parse_json = query_config.custom['parse_json']
        do_post = query_config.custom['do_post']
        format_ = query_config.custom['format']
        try:
            return self._sql_client.send(formatted_statement, parse_json=parse_json, do_post=do_post, format= format_)

        except CartoException as e:
            raise LongitudeQueryCannotBeExecutedException
