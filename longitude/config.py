"""
Entry point for app configuration. Any module requiring a configuration
parameter should import it from this module.

The module defines a series of basic configuration attributes (listed in
_BASE_CONFIG_PARAMS) whose value will be retrieved from the system
environment. Of these values, only SECRET_KEY is compulsory.

The module then tries to import the global module "settings". This module
should include a
"""

import sys
import os
from itertools import chain

try:
    from settings import config as user_config
except ImportError:
    user_config = []

_BASE_CONFIG_PARAMS = [
    #(<CONF_NAME>, <CONF_TYPE>, <CONF_DEFAULT_VALUE>)
    ('CARTO_API_KEY', str, ''),
    ('CARTO_USER', str, ''),

    ('DB_NAME', str, 'postgres'),
    ('DB_USER', str, 'postgres'),
    ('DB_PASSWORD', str, 'postgres'),
    ('DB_HOST', str, 'postgis'),
    ('DB_PORT', int, 5432),
    ('DB_SCHEMA', str, 'public'),

    ('REDIS_HOST', str, 'redis'),
    ('REDIS_PORT', int, 6379),
    ('REDIS_DB', int, 0),

    ('DEBUG', bool, '1'),
    ('LOG_LEVEL', str, 'INFO'),

    ('CACHE', bool, '1'),
    # Expire time in seconds (default 15 minutes): 15*60=900
    ('CACHE_EXPIRE', int, 900),

    ('SECRET_KEY', str, None),

    ('API_TOKEN_EXPIRATION', int, 900),
    ('AUTH_TOKEN_DOBLE_CHECK', bool, False),
    ('AUTH_USER_TABLE', str, 'users'),
    ('AUTH_TOKEN_TABLE', str, 'users_token'),
]

_module = sys.modules[__name__]

for conf_param in chain(_BASE_CONFIG_PARAMS, user_config):

    if len(conf_param) not in (2, 3):
        raise RuntimeError('Configuration param %s must have 2 or 3 elements.' % str(conf_param))

    config_param_name, ctype = conf_param[:2]

    if len(conf_param) == 3:
        default = conf_param[2]
    else:
        default = None

    value = os.environ.get(config_param_name, default)

    if value is None:
        raise RuntimeError('Missing required parameter: ' + config_param_name)

    if type == bool:
        value = value if isinstance(value, bool) else \
            value == '1'
    else:
        value = ctype(value)

    setattr(_module, config_param_name, value)
