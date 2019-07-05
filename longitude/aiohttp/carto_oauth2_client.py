import jwt
import logging
from aiohttp import web
from aioauth_client import OAuth2Client
from datetime import datetime, timedelta

from longitude.core.common.helpers import add_url_params


class AiohttpCartoOAuth2Client(OAuth2Client):
    """Carto OAuth2 client implementation.

    Two 'login_process' and 'refresh_token' helper functions are provided to facilitate the
    login process implementation for most general cases.
    """

    def __init__(self, client_id, client_secret, base_url, scope='offline'):
        super().__init__(self, client_id, client_secret, scope=scope)
        self.name = 'carto'
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret

        self.base_url = base_url
        self.access_token_url = f'https://{base_url}/oauth2/token'
        self.authorize_url = f'https://{base_url}/oauth2/authorize'
        self.user_info_url = f'https://{base_url}/api/v4/me'

        self.log = logging.getLogger(self.__class__.__module__)

    @staticmethod
    def user_parse(data):
        """Parse information from provider."""
        return data

    async def login_process(
        self, request, session_register_cb=None, referer_url_params_cb=None, error_cb=None, state={}
    ):
        """Login helper for Carto OAuth2 process.

        If the login process was successful, then two options:
            * If request.headers.get('Referer') was set, then the function will redirect to this URL adding a few
              arguments to the URL (@see referer_url_params_cb below).
            * Othercase the session data will be returned as JSON with `web.json_response(session_data)`

        In case of errors, the error callback will be called (@see error_cb below), or an error response will
        be returned as JSON with `aiohttp.web.json_response` function.

        @see `longitude/samples` folder for usage examples.

        @param request - AioHttp request object.

        @param session_register_cb - Callback function which receives three params:
            * access_token (str)
            * session_data (dict): you can use this data to store and maintain a session wherever you need to.
            * state (dict): state obj, with the additional 'referer' http header if present. It also can be
              provided along with the 'state' (dict) parameter of the login_process function.

            This function can also return a dict with additional custom parameters (i.e: user_role, user_group, etc.),
            which will be appended to the session_data that will be received by the referer_url_params_cb.

        @param referer_url_params_cb - If provided, it will receive the session_data and must return a dict with
            the fields you need to pass to the front-end success login page. This fields will be appended
            as parameters to the redirected URL.

            The default behaviour returns the following fields from the session_data:
            'username', 'access_token', 'expires_in'

        @param error_cb - If provided this function will be called in the case we receive an error from Carto OAuth
            service. This function will receive a dictionary with the 'error' parameter, and also may include
            'error_description' and 'error_uri'. More info about OAuth2 errors here:
            https://www.oauth.com/oauth2-servers/server-side-apps/possible-errors/

            The default behaviour is to return a JSON response by using the aiohttp.web.json_response function.

        @param state - Dictionary with custom data that will be added to the 'state' encoded string that will
            be shared with the OAuth endpoint. It will be received back in the session_register_cb function as the
            third parameter.
        """
        if 'error' in request.query:
            error_func = error_cb or web.json_response
            return error_func({**request.query})

        # After login, just redirect back here:
        self.params['redirect_uri'] = f'https://{request.host}{request.path}'

        # If we're not already authorized:
        #   (request.query must have a 'code' key (shared_key = 'code' here))
        if self.shared_key not in request.query:
            state_str = self.create_encoded_state(
                request,
                state={'referer': request.headers.get('Referer'), **(state or {})},
            )
            return web.HTTPFound(self.get_authorize_url(state=state_str))

        # Getting back and checking the state parameter:
        state_data = self.get_state(request)
        if not state_data:
            return web.HTTPUnauthorized()

        # We've a 'code' parameter here, so let's use it to get access token, and user info
        oauth_token, meta = await self.get_access_token(request.query)
        self.user_info_url = meta['user_info_url']

        _, user_info = await self.user_info(params={'api_key': oauth_token})
        meta['expires_in'] = int(meta['expires_in'])
        session_data = {
            'user_info': user_info,
            **meta
        }

        if session_register_cb is not None:
            custom_session_data = await session_register_cb(oauth_token, session_data, state)
            session_data.update(custom_session_data or {})

        # Getting the previously stored Referer URL.
        # If it's present, we have an URL to which redirect back:
        if state_data.get('referer'):
            referer_url = state_data.get('referer')
            get_referer_url_params = referer_url_params_cb or self.default_referer_params
            redirect_uri = add_url_params(referer_url, get_referer_url_params(session_data))
            return web.HTTPFound(redirect_uri)

        # We come from Postman or similar, so just returns the user info:
        return web.json_response({**session_data})

    async def refresh_token(self, session_data):
        """Refresh OAuth token by using the session_data['refresh_token'] returned by the Carto OAuth2 service.

        **Note** you must have included the 'offline' value along with the "scope" in order to get this
        'refresh_token' parameter in the session_data object.
        """
        oauth_token, meta = await self.get_access_token(
            code=session_data['refresh_token'],
            grant_type='refresh_token'
        )
        meta['expires_in'] = int(meta['expires_in'])
        new_session_data = {**session_data, **meta}

        return oauth_token, new_session_data

    def create_encoded_state(self, request, state={}):
        payload = {
            **state,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=3)
        }
        # Let's use the same secret for this :)
        secret = self.client_secret

        encoded_jwt = jwt.encode(payload, secret, algorithm='HS256')
        return encoded_jwt

    def get_state(self, request):
        try:
            secret = self.client_secret
            state_str = request.query.get('state')
            return jwt.decode(state_str, secret, algorithms=['HS256'])
        except jwt.exceptions.ExpiredSignatureError:
            self.log.warning('Expired state token has been used: {}'.format(state_str))
            return None
        except Exception as err:
            self.log.exception(err)
            return None

    def default_referer_params(self, session_data):
        return {
            'username': session_data['user_info']['username'],
            'access_token': session_data['access_token'],
            'expires_in': session_data['expires_in']
        }
