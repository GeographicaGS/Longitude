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

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))  # noqa
from longitude.core.caches.ram import RamCache
from longitude.core.data_sources.carto import CartoDataSource
from longitude.samples.config import config

# import logging
# logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":

    ram_cache = RamCache()
    ds = CartoDataSource(
        user=config['carto_user'],
        api_key=config['carto_api_key'],
        options={
            'cache': ram_cache
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
    start = time.time()
    data = ds.query(REPEATED_QUERY, cache=False)
    elapsed = time.time() - start
    print('It took %s with disabled cache (per-query)' % str(elapsed))
    print('Uses cache? ' + str(data.from_cache))

    print('If you see decreasing times it is probably because CARTOs cache doing its job!')
