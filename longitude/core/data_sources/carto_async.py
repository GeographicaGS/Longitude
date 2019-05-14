import aiohttp
from cartoasync import Auth, SQLClient

from carto.exceptions import CartoException

from ..common.query_response import LongitudeQueryResponse
from .base_async import AsyncDataSource
from ..common.exceptions import LongitudeQueryCannotBeExecutedException


class CartoAsyncDataSource(AsyncDataSource):
    SUBDOMAIN_URL_PATTERN = "https://%s.carto.com"
    ON_PREMISES_URL_PATTERN = "https://%s/user/%s"
    DEFAULT_API_VERSION = 'v2'

    def __init__(self, user, api_key, options={}):
        super().__init__(options)

        self.format = options.get('format', 'json')
        self.base_url_option = options.get('base_url', '')
        self.api_version = options.get('api_version', self.DEFAULT_API_VERSION)
        self.session = options.get('session', None)

        self.user = user
        self.api_key = api_key
        self.base_url = self._generate_base_url(user, self.base_url_option)

        self._auth_client = Auth(api_key=api_key, base_url=self.base_url)
        self._sql_client = SQLClient(self._auth_client, session=self.session)

    # These three methods allows the ussage with the 'async with'. i.e:
    #       async with CartoAsyncDataSource(**params) as ds:
    #           ...
    # If you don't want to pass your own 'session' on the constructor method,
    # this is the other way for the SQLClient to share the same ClientSession between requests.
    async def __aenter__(self, user=None, api_key=None, options={}):
        await self._init_session()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()

    async def _init_session(self):
        # async with aiohttp.ClientSession() as session:
        self.session = aiohttp.ClientSession()
        self._sql_client = SQLClient(self._auth_client, session=self.session)

    def _generate_base_url(self, user, base_url_option):
        if base_url_option:
            base_url = self.ON_PREMISES_URL_PATTERN % (base_url_option, user)
        else:
            base_url = self.SUBDOMAIN_URL_PATTERN % user
        return base_url

    async def execute_query(self, query_template, params, query_config, **opts):
        params = {k: "'" + v + "'" for k, v in params.items()}
        formatted_query = query_template % params

        try:
            return await self._sql_client.send(
                formatted_query,
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
