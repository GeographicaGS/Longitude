"""It's a good practice to put all config loading in the same file.

The `environs` library does a good job getting environment variables,
and it's quite straight forward:

    @see https://pypi.org/project/environs/

However, if you ever need to change the environment vars by let's say,
a .conf file, or a database-stored config, or whatever, this centralized
approach allows you to change the whole config loading process by only
editing this file :)

As a little example, this is the config object shared by all sample scripts
in this folder:
"""

from environs import Env

env = Env()

config = {
    'carto_user': env('CARTO_USER'),
    'carto_api_key': env('CARTO_API_KEY'),
    'pg_user': env('PG_USER'),
    'pg_password': env('PG_PASSWORD'),
    'debug': env.bool('DEBUG', False),
    'oauth': {
        'client_id': env('OAUTH_CLIENT_ID'),
        'client_secret': env('OAUTH_CLIENT_SECRET'),
        'base_url': env('OAUTH_BASE_URL'),
        'scope': env('OAUTH_SCOPE', 'offline'),

        'pem_file': env('SSL_PEM_FILE'),
        'key_file': env('SSL_KEY_FILE')
    }
}
