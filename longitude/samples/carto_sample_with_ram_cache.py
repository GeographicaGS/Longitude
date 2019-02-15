"""
██╗  ██╗ ██████╗ ██╗    ██╗    ████████╗ ██████╗     ██╗   ██╗███████╗███████╗    ████████╗██╗  ██╗██╗███████╗
██║  ██║██╔═══██╗██║    ██║    ╚══██╔══╝██╔═══██╗    ██║   ██║██╔════╝██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝██╗
███████║██║   ██║██║ █╗ ██║       ██║   ██║   ██║    ██║   ██║███████╗█████╗         ██║   ███████║██║███████╗╚═╝
██╔══██║██║   ██║██║███╗██║       ██║   ██║   ██║    ██║   ██║╚════██║██╔══╝         ██║   ██╔══██║██║╚════██║██╗
██║  ██║╚██████╔╝╚███╔███╔╝       ██║   ╚██████╔╝    ╚██████╔╝███████║███████╗       ██║   ██║  ██║██║███████║╚═╝
╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝        ╚═╝    ╚═════╝      ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝   

Fill the needed environment variables using LONGITUDE__ as prefix!
"""

import time
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from longitude.core.caches.ram import RamCache
from longitude.core.data_sources.base import LongitudeRetriesExceeded
from longitude.core.data_sources.carto import CartoDataSource

if __name__ == "__main__":
    # This will throw a log warning as we are passing a password to the RamCache config and it does not expect it
    ds = CartoDataSource(config='carto_main', cache_class=RamCache)
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

            # Data is the same...
            assert str(data) == str(cached_data)

            # You can also disable the cache for a while (nothing gets read or written)
            ds.disable_cache()
            start = time.time()
            data = ds.query(REPEATED_QUERY)
            elapsed = time.time() - start
            print('It took %s with disabled cache' % str(elapsed))
            print('Uses cache? ' + str(data.from_cache))
            ds.enable_cache()

            # Or disable specific queries via query_config (nothing gets read or written)
            query_config = ds.copy_default_query_config()
            start = time.time()
            data = ds.query(REPEATED_QUERY, query_config=query_config, cache=False)
            elapsed = time.time() - start
            print('It took %s with disabled cache (per-query)' % str(elapsed))
            print('Uses cache? ' + str(data.from_cache))

            print('If you see decreasing times it is probably because CARTOs cache doing its job!')

        except LongitudeRetriesExceeded:
            print("Too many retries and no success...")
    else:
        print("Data source is not properly configured.")
