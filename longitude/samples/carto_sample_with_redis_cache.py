"""
██╗  ██╗ ██████╗ ██╗    ██╗    ████████╗ ██████╗     ██╗   ██╗███████╗███████╗    ████████╗██╗  ██╗██╗███████╗
██║  ██║██╔═══██╗██║    ██║    ╚══██╔══╝██╔═══██╗    ██║   ██║██╔════╝██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝██╗
███████║██║   ██║██║ █╗ ██║       ██║   ██║   ██║    ██║   ██║███████╗█████╗         ██║   ███████║██║███████╗╚═╝
██╔══██║██║   ██║██║███╗██║       ██║   ██║   ██║    ██║   ██║╚════██║██╔══╝         ██║   ██╔══██║██║╚════██║██╗
██║  ██║╚██████╔╝╚███╔███╔╝       ██║   ╚██████╔╝    ╚██████╔╝███████║███████╗       ██║   ██║  ██║██║███████║╚═╝
╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝        ╚═╝    ╚═════╝      ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝

Fill the needed environment variables using LONGITUDE__ as prefix!

There is a cache entry in the docker-compose.yaml file. You can use it to run a local Redis container to test this:

> sudo docker-compose up -d cache

Also, you can connect to that container and check the cache using the CLI while running this program.

> sudo docker exec -it longitude_cache_1 redis-cli

"""

import time
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))  # noqa
from longitude.core.common.helpers import DisabledCache
from longitude.core.caches.redis import RedisCache
from longitude.core.data_sources.carto import CartoDataSource
from longitude.samples.config import config

if __name__ == "__main__":

    redis_cache = RedisCache()
    ds = CartoDataSource(
        user=config['carto_user'],
        api_key=config['carto_api_key'],
        options={
            'cache': redis_cache
        }
    )

    REPEATED_QUERY = 'select * from country_population limit 30'
    start = time.time()
    data = ds.query(REPEATED_QUERY)
    elapsed = time.time() - start
    print("It took %s without cache" % elapsed)
    print('Uses cache? ' + str(data.from_cache))

    # Repeated read queries return cached values
    start_with_cache = time.time()
    cached_data = ds.query(REPEATED_QUERY)
    elapsed_with_cache = time.time() - start_with_cache
    print("It took %s with cache" % elapsed_with_cache)
    print('Uses cache? ' + str(cached_data.from_cache))

    # You can also disable the cache for a while (nothing gets read or written)
    with DisabledCache(ds):
        start = time.time()
        data = ds.query(REPEATED_QUERY)
        elapsed = time.time() - start
        print('It took %s with disabled cache' % str(elapsed))
        print('Uses cache? ' + str(data.from_cache))

    start = time.time()
    data = ds.query(REPEATED_QUERY, cache=False)
    elapsed = time.time() - start
    print('It took %s with disabled cache (per-query)' % str(elapsed))
    print('Uses cache? ' + str(data.from_cache))

    print('If you see decreasing times it is probably because CARTOs cache doing its job!')

    # As Redis is persistent for this script, we flush it after execution so next run does not hit at start
    ds.flush_cache()
