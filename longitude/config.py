import os

cfg = {
    'POSTGRES_HOST': os.environ.get('POSTGRES_HOST', ''),
    'POSTGRES_PORT': os.environ.get('POSTGRES_PORT', ''),
    'POSTGRES_DB': os.environ.get('POSTGRES_DB', ''),
    'POSTGRES_USER': os.environ.get('POSTGRES_USER', ''),
    'POSTGRES_PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
    'CARTO_API_KEY': os.environ.get('CARTO_API_KEY', ''),
    'CARTO_USER': os.environ.get('CARTO_USER', ''),
    'CARTO_ONPREMISES_URL': os.environ.get('CARTO_ONPREMISES_URL'),
    'DATABASE_MODEL': os.environ.get('DATABASE_MODEL', 'CARTO'),
    'REDIS_PORT': os.environ.get('REDIS_PORT', 6379),
    'REDIS_HOST': os.environ.get('REDIS_HOST', 'localhost'),
    'REDIS_DB': os.environ.get('REDIS_DB', 0),
    'CACHE_EXPIRE':  os.environ.get('CARTO_CACHE_EXPIRE', 900),
    'CACHE': bool(int(os.environ.get('CARTO_CACHE', 0))),
    'AUTH_TOKEN_EXPIRATION': int(os.environ.get('API_TOKEN_EXPIRATION', 60*15)),
    'AUTH_TOKEN_DOBLE_CHECK': bool(int(os.environ.get('AUTH_TOKEN_DOBLE_CHECK', 0))),
    'AUTH_USER_TABLE': os.environ.get('AUTH_USER_TABLE', 'users'),
    'AUTH_TOKEN_TABLE': os.environ.get('AUTH_TOKEN_TABLE', 'users_tokens')
}


# Add extra JWT identity fields

extra_jwt_identity_fields = {key: value for (key, value) in os.environ.items() if key.startswith('JWT_IDENTITY_')}
cfg['EXTRA_JWT_IDENTITY_FIELDS'] = extra_jwt_identity_fields


