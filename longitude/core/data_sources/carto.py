from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sql import BatchSQLClient, SQLClient

from ..common.query_response import LongitudeQueryResponse
from .base import DataSource, LongitudeQueryCannotBeExecutedException


class CartoDataSource(DataSource):
    SUBDOMAIN_URL_PATTERN = "https://%s.carto.com"
    ON_PREMISE_URL_PATTERN = "https://%s/user/%s"
    _default_config = {
        'api_version': 'v2',
        'uses_batch': False,
        'on_premise_domain': '',
        'api_key': '',
        'user': '',
        'cache': None
    }

    def __init__(self, config='', cache_class=None, cache=None):
        super().__init__(config=config, cache_class=cache_class, cache=cache)

        self.set_custom_query_default('do_post', False)
        self.set_custom_query_default('parse_json', True)
        self.set_custom_query_default('format', 'json')

        # Carto Context for DataFrame handling
        self._carto_context = None

        # Carto client for COPYs
        self._copy_client = None

        self._auth_client = APIKeyAuthClient(api_key=self.get_config('api_key'), base_url=self.base_url)
        self._sql_client = SQLClient(self._auth_client, api_version=self.get_config('api_version'))

        # TODO: We could create the batch client instance in the first use instead of getting a config field
        self._batch_client = None
        if self.get_config('uses_batch'):
            self._batch_client = BatchSQLClient(self._auth_client)

    @property
    def is_ready(self):
        if super().is_ready:
            sql_setup_ready = self._sql_client is not None
            batch_setup_ready = not self.get_config('uses_batch') or (self._batch_client is not None)
            is_ready = sql_setup_ready and batch_setup_ready and self.get_config('user') != ''
            return is_ready
        else:
            return False

    @property
    def cc(self):
        """
        Creates and returns a CartoContext object to work with Panda Dataframes
        :return:
        """
        # TODO: The CartoContext documentaton says that SSL must be disabled sometimes if an on premise host is used
        #  We are not taking this into account. It would need to create a requests.Session() object, set its SSL
        #  to false and pass it to the CartoContext init.
        import cartoframes
        if self._carto_context is None:
            self._carto_context = cartoframes.CartoContext(base_url=self.base_url, api_key=self.get_config('api_key'))
        return self._carto_context

    @property
    def base_url(self):
        return self._generate_base_url()

    def _generate_base_url(self, user=None):
        if user is None:
            user = self.get_config('user')
        on_premise_domain = self.get_config('on_premise_domain')
        if on_premise_domain:
            base_url = self.ON_PREMISE_URL_PATTERN % (on_premise_domain, user)
        else:
            base_url = self.SUBDOMAIN_URL_PATTERN % user
        return base_url

    def execute_query(self, query_template, params, needs_commit, query_config, **opts):
        # TODO: Here we are parsing the parameters and taking responsability for it. We do not make any safe parsing as
        #  this will be used in a backend-to-backend context and we build our own queries.
        #  ---
        #  This is also problematic as quoting is not done and relies in the query template
        #  ---
        #  Can we use the .mogrify method in psycopg2 to render a query as it is going to be executed ? -> NO
        #  ->  .mogrify is a cursor method but in CARTO connections we lack a cursor.
        #  ---
        #  There is an open issue in CARTO about having separated parameters and binding them in the server:
        #  https://github.com/CartoDB/Geographica-Product-Coordination/issues/57
        params = {k: "'" + v + "'" for k, v in params.items()}
        formatted_query = query_template % params

        parse_json = query_config.custom['parse_json']
        do_post = query_config.custom['do_post']
        format_ = query_config.custom['format']
        try:
            return self._sql_client.send(formatted_query, parse_json=parse_json, do_post=do_post, format=format_)

        except CartoException as e:
            raise LongitudeQueryCannotBeExecutedException(str(e))

    def parse_response(self, response):
        return LongitudeQueryResponse(
            rows=response['rows'],
            fields=response['fields'],
            profiling={
                'response_time': response['time'],
                'total_rows': response['total_rows']
            }
        )

    def copy_from(self, data, filepath, to_table):
        if self._copy_client is None:
            from carto.sql import CopySQLClient
            self._copy_client = CopySQLClient(self._auth_client)
        headers = data.readline().decode('utf-8')
        data.seek(0)
        from_query = 'COPY %s (%s) FROM stdin WITH (FORMAT csv, HEADER true)' % (to_table, headers)
        return self._copy_client.copyfrom_file_object(from_query, data)

    def read_dataframe(self, table_name='', *args, **kwargs):
        return self.cc.read(table_name=table_name, *args, **kwargs)

    def query_dataframe(self, query='', *args, **kwargs):
        return self.cc.query(query=query, *args, **kwargs)

    def write_dataframe(self, df, table_name='', *args, **kwargs):
        return self.cc.write(df=df, table_name=table_name, *args, **kwargs)
