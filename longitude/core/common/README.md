# Common modules

## Environment Variables

Longitude is configured by default to read environment variables that start with `LONGITUDE__`. Such variables will be parsed into nested dictionaries using '__' (double underscore) as default separator for depths.

Example:

```bash
LONGITUDE__CARTO_INDOOR__USER=resouce37
LONGITUDE__CARTO_INDOOR__API_KEY=b3r3nj3n4
LONGITUDE__CARTO_INDOOR__CACHE__PASSWORD=r4b1ll0_d3_p454
LONGITUDE__TESTING=yes
```

Generates this `EnvironmentConfiguration` (which is imported as `LConfig` here)

```python
from longitude.core.common.config import EnvironmentConfiguration as LConfig

config = LConfig.get()

# config content is the same as:

config = {
    'carto_indoor': {
        'user': 'resource37',
        'api_key': 'b3r3nj3n4',
        'cache': {
            'password': 'r4b1ll0_d3_p4545'
        }
    }
}

```

You can access to children using a dot notation for fully qualified names, like:

```python
from longitude.core.common.config import EnvironmentConfiguration as LConfig

redis_password = LConfig.get('carto_indoor.cache.password')
```

You can also overwrite configurations or add custom fields after LConfig has been instanced at least once:

```python
from longitude.core.common.config import EnvironmentConfiguration as LConfig

root_config = LConfig.get()
root_config['custom'] = {
    'custom_value': 'you can add me!'
}

some_text = LConfig.get('custom.custom_value')  # == 'you can add me!'

```

Using this you can, for example, define a common cache config and share it among many sub configurations:

```python
from longitude.core.common.config import EnvironmentConfiguration as LConfig

shared_cache_config = LConfig.get('shared_cache')

carto_main_config= LConfig.get('carto_main')
carto_main_config['cache'] = shared_cache_config 

api_main_config=LConfig.get('flask')
api_main_config['cache'] = shared_cache_config

```

### Custom configuration object.

You can create your own configuration class deriving from `EnvironmentConfiguration` and, for example, configure a different prefix or a different separator.

This can be used to check for different environment variable sets.