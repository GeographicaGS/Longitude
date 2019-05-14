import cartoframes
from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sql import BatchSQLClient, SQLClient

from ..common.query_response import LongitudeQueryResponse
from .base import DataSource, LongitudeQueryCannotBeExecutedException


class CartoDataSource(DataSource):
    SUBDOMAIN_URL_PATTERN = "https://%s.carto.com"
    ON_PREMISES_URL_PATTERN = "https://%s/user/%s"
    DEFAULT_API_VERSION = 'v2'

    def __init__(self, user, api_key, options={}):
        super().__init__(options)

        self.do_post = options.get('do_post', False)
        self.parse_json = options.get('parse_json', True)
        self.format = options.get('format', 'json')
        self.base_url_option = options.get('base_url', '')
        self.api_version = options.get('api_version', self.DEFAULT_API_VERSION)
        self.batch = options.get('batch', False)

        self.user = user
        self.api_key = api_key
        self.base_url = self._generate_base_url(user, self.base_url_option)

        # Carto Context for DataFrame handling
        self._carto_context = None

        # Carto client for COPYs
        self._copy_client = None

        self._auth_client = APIKeyAuthClient(api_key=api_key, base_url=self.base_url)
        self._sql_client = SQLClient(self._auth_client, api_version=self.api_version)

        self._batch_client = None
        if self.batch:
            self._batch_client = BatchSQLClient(self._auth_client)

    @property
    def cc(self):
        """
        Creates and returns a CartoContext object to work with Panda Dataframes
        :return:
        """
        # TODO: The CartoContext documentaton says that SSL must be disabled sometimes if an on
        #  premise host is used.
        #  We are not taking this into account. It would need to create a requests.Session()
        #  object, set its SSL to false and pass it to the CartoContext init.
        if self._carto_context is None:
            self._carto_context = cartoframes.CartoContext(
                base_url=self.base_url, api_key=self.api_key
            )
        return self._carto_context

    def _generate_base_url(self, user, base_url_option):
        if base_url_option:
            base_url = self.ON_PREMISES_URL_PATTERN % (base_url_option, user)
        else:
            base_url = self.SUBDOMAIN_URL_PATTERN % user
        return base_url

    def execute_query(self, query_template, params, query_config, **opts):
        # TODO: Here we are parsing the parameters and taking responsability for it. We do not make
        #  any safe parsing as this will be used in a backend-to-backend context and we build our
        #  own queries.
        #  ---
        #  This is also problematic as quoting is not done and relies in the query template
        #  ---
        #  Can we use the .mogrify method in psycopg2 to render a query as it is going to be
        #  executed ? -> NO
        #   ->  .mogrify is a cursor method but in CARTO connections we lack a cursor.
        #  ---
        #  There is an open issue in CARTO about having separated parameters and binding them in
        #  the server:
        #   https://github.com/CartoDB/Geographica-Product-Coordination/issues/57
        params = {k: "'" + v + "'" for k, v in params.items()}
        formatted_query = query_template % params

        try:
            return self._sql_client.send(
                formatted_query,
                parse_json=self.parse_json,
                do_post=self.do_post,
                format=self.format
            )

        except CartoException as e:
            raise LongitudeQueryCannotBeExecutedException(str(e))

    def parse_response(self, response):
        return LongitudeQueryResponse(
            rows=response['rows'],
            fields=response['fields'],
            meta={
                'response_time': response.get('time'),
                'total_rows': response.get('total_rows')
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
