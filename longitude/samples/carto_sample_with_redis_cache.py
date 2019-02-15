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

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from longitude.core.common.helpers import DisabledCache
from longitude.core.caches.redis import RedisCache
from longitude.core.common.exceptions import LongitudeRetriesExceeded
from longitude.core.data_sources.carto import CartoDataSource

if __name__ == "__main__":

    ds = CartoDataSource(config='carto_main', cache_class=RedisCache)
    if ds.is_ready:
        try:

            REPEATED_QUERY = 'select * from county_population limit 30'
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

            # Or disable specific queries via query_config (nothing gets read or written)
            query_config = ds.copy_default_query_config()
            start = time.time()
            data = ds.query(REPEATED_QUERY, query_config=query_config, cache=False)
            elapsed = time.time() - start
            print('It took %s with disabled cache (per-query)' % str(elapsed))
            print('Uses cache? ' + str(data.from_cache))

            print('If you see decreasing times it is probably because CARTOs cache doing its job!')

            # As Redis is persistent for this script, we flush it after execution so next run does not hit at start
            ds.flush_cache()

        except LongitudeRetriesExceeded:
            print("Too many retries and no success...")
    else:
        print("Data source is not properly configured.")
