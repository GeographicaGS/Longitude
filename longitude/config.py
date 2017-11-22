import os

cfg = {
    'CARTO_API_KEY': os.environ.get('CARTO_API_KEY', ''),
    'CARTO_USER': os.environ.get('CARTO_USER', ''),
    'REDIS_PORT': os.environ.get('REDIS_PORT', 6379),
    'REDIS_HOST': os.environ.get('REDIS_HOST', 'localhost'),
    'REDIS_DB': os.environ.get('REDIS_DB', 0),
    'CACHE_EXPIRE':  os.environ.get('CARTO_CACHE_EXPIRE', 900),
    'CACHE': bool(int(os.environ.get('CARTO_CACHE', 0))),
    'AUTH_TOKEN_EXPIRATION': int(os.environ.get('API_TOKEN_EXPIRATION', 60*15)),
    'AUTH_TOKEN_DOBLE_CHECK': bool(int(os.environ.get('AUTH_TOKEN_DOBLE_CHECK', 0))),
    'AUTH_USER_TABLE': os.environ.get('AUTH_USER_TABLE','users'),
    'AUTH_TOKEN_TABLE': os.environ.get('AUTH_TOKEN_TABLE','users_tokens')
}
