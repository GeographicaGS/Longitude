"""
██╗  ██╗ ██████╗ ██╗    ██╗    ████████╗ ██████╗     ██╗   ██╗███████╗███████╗    ████████╗██╗  ██╗██╗███████╗
██║  ██║██╔═══██╗██║    ██║    ╚══██╔══╝██╔═══██╗    ██║   ██║██╔════╝██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝██╗
███████║██║   ██║██║ █╗ ██║       ██║   ██║   ██║    ██║   ██║███████╗█████╗         ██║   ███████║██║███████╗╚═╝
██╔══██║██║   ██║██║███╗██║       ██║   ██║   ██║    ██║   ██║╚════██║██╔══╝         ██║   ██╔══██║██║╚════██║██╗
██║  ██║╚██████╔╝╚███╔███╔╝       ██║   ╚██████╔╝    ╚██████╔╝███████║███████╗       ██║   ██║  ██║██║███████║╚═╝
╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝        ╚═╝    ╚═════╝      ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝   

You must create a 'carto_sample_config.py' file at this folder with the needed fields (look at the import)
That file will be ignored in git, so do not worry about pushing credentials anywhere (but BE CAREFUL!)
DO NOT REPLACE THIS WITH HARD CODED CREDENTIALS EVER AND ALWAYS REVIEW YOUR COMMITS!

There is a cache entry in the docker-compose.yaml file. You can use it to run a local Redis container to test this:

> sudo docker-compose up -d cache

Also, you can connect to that container and check the cache using the CLI while running this program.

> sudo docker exec -it longitude_cache_1 redis-cli

"""

import time
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core.caches.redis import RedisCache, RedisCacheConfig
from src.core.data_sources.base import LongitudeRetriesExceeded
from src.core.data_sources.carto import CartoDataSource
from src.samples.carto_sample_config import CARTO_API_KEY, CARTO_USER, CARTO_TABLE_NAME

if __name__ == "__main__":
    config = {
        'api_key': CARTO_API_KEY,
        'user': CARTO_USER,
        'cache': RedisCacheConfig(password='as')
    }

    ds = CartoDataSource(config, cache_class=RedisCache)
    ds.setup()
    if ds.is_ready:
        try:

            REPEATED_QUERY = 'select * from %s limit 30' % CARTO_TABLE_NAME
            start = time.time()
            data = ds.query(REPEATED_QUERY)
            elapsed = time.time() - start
            print("It took %s without cache" % elapsed)
            print('Uses cache? ' + str(data.comes_from_cache))

            # Repeated read queries return cached values
            start_with_cache = time.time()
            cached_data = ds.query(REPEATED_QUERY)
            elapsed_with_cache = time.time() - start_with_cache
            print("It took %s with cache" % elapsed_with_cache)
            print('Uses cache? ' + str(cached_data.comes_from_cache))

            # Data is the same...
            assert str(data) == str(cached_data)

            # You can also disable the cache for a while (nothing gets read or written)
            ds.disable_cache()
            start = time.time()
            data = ds.query(REPEATED_QUERY)
            elapsed = time.time() - start
            print('It took %s with disabled cache' % str(elapsed))
            print('Uses cache? ' + str(data.comes_from_cache))
            ds.enable_cache()

            # Or disable specific queries via query_config (nothing gets read or written)
            query_config = ds.copy_default_query_config()
            query_config.use_cache = False
            start = time.time()
            data = ds.query(REPEATED_QUERY, query_config=query_config)
            elapsed = time.time() - start
            print('It took %s with disabled cache (per-query)' % str(elapsed))
            print('Uses cache? ' + str(data.comes_from_cache))

            print('If you see decreasing times it is probably because CARTOs cache doing its job!')

            # As Redis is persistent for this script, we flush it after execution so next run does not hit at start
            ds.flush_cache()

        except LongitudeRetriesExceeded:
            print("Too many retries and no success...")
    else:
        print("Data source is not properly configured.")
