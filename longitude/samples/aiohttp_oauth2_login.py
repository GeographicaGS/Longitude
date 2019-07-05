import os
import sys
import ssl
from aiohttp import web

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))  # noqa
from longitude.aiohttp.carto_oauth2_client import AiohttpCartoOAuth2Client
from longitude.samples.config import config

"""
    Minimal Carto-OAuth2 working example.
    More details about this at `longitude/aiohttp/carto_oauth2_client.py`

    You'll need an onpremises instance of Carto and a pre-configured app:
    @see https://docs.google.com/document/d/1dvdZuBF7J5fQiV6Wh1s40_gPAqFjIwtgDu1E6VBav5s

    This example contains the following endpoints:

        Login:
            GET /api/v1/users/auth
        Refresh token:
            GET /api/v1/users/auth/refresh
        Logout:
            GET /api/v1/users/logout  /  HEADER Authorization: <access_token>

        Testing auth middleware and authenticated endpoint:
            GET /api/v1/data/private  /  HEADER Authorization: <access_token>
"""


login_routes = web.RouteTableDef()
private_routes = web.RouteTableDef()

# We'll need ssl here, so we can use the snakeoil cert for example:
pem_file = config['oauth']['pem_file']
key_file = config['oauth']['key_file']


# OAuth client config:
def get_oauth_client():
    return AiohttpCartoOAuth2Client(
        client_id=config['oauth']['client_id'],
        client_secret=config['oauth']['client_secret'],
        base_url=config['oauth']['base_url'],
        scope=config['oauth']['scope']
    )


# Login management:
# ------------------
@login_routes.get('/api/v1/users/auth')
async def auth_get(request):
    oauth_client = get_oauth_client()
    return await oauth_client.login_process(request, session_register_cb=set_session)


@login_routes.get('/api/v1/users/auth/refresh')
async def auth_refresh(request):
    access_token = request.headers.get('Authorization') or request.headers.get('x-auth-token')
    if not access_token:
        return web.HTTPUnauthorized()

    session_data = await get_session(access_token)
    if session_data:
        oauth_client = get_oauth_client()
        oauth_token, new_session_data = await oauth_client.refresh_token(session_data)
        await set_session(oauth_token, new_session_data)

        return web.json_response(new_session_data)

    return web.HTTPUnauthorized()


@login_routes.get('/api/v1/users/logout')
async def user_logout(request):
    access_token = request.headers.get('Authorization') or request.headers.get('x-auth-token')
    await delete_session(access_token)
    return web.json_response({'status': 'ok', 'msg': 'Bye'})
    # In order to logout from Carto, you must redirect to the following URL instead:
    # web.HTTPFound(f'https://{base_url}/user/{username}/logout')
# End login management ------------------


# Auth middleware and authenticated endpoints:
@web.middleware
async def auth_middleware(request, handler):
    # avoid 'OPTIONS' requests authentication
    if request.method.lower() in ['options']:
        return await handler(request)

    # Checks the user has an active session:
    access_token = request.headers.get('Authorization') or request.headers.get('x-auth-token')
    user_session = await get_session(access_token) if access_token else None
    if user_session:
        # Check permissions here if you wish...
        request.session_data = user_session
        return await handler(request)

    return web.HTTPUnauthorized()


@private_routes.get('/private')
async def private_handle(request):
    username = request.session_data['user_info']['username']
    return web.json_response({'status': 'ok', 'msg': f'Hello, {username}'})
# End auth middleware... ------------------


# Session data would be stored on redis or cookies, or whatever, this is just a naive example:
global_sesion_data = {}


async def get_session(access_token):
    global global_sesion_data
    return global_sesion_data.get(access_token, {})


async def delete_session(access_token):
    global global_sesion_data
    del global_sesion_data[access_token]


async def set_session(access_token, session_data, state={}):
    global global_sesion_data
    global_sesion_data[access_token] = session_data
# -- end session management


# Main app:
app = web.Application()
app.add_routes(login_routes)

# Private subapp(s)
subapp = web.Application()
subapp.add_routes(private_routes)
subapp.middlewares.extend([auth_middleware])


app.add_subapp('/api/v1/data', subapp)

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(pem_file, key_file)

web.run_app(app, ssl_context=ssl_context, port=8080)
