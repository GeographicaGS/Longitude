"""
██╗  ██╗ ██████╗ ██╗    ██╗    ████████╗ ██████╗     ██╗   ██╗███████╗███████╗    ████████╗██╗  ██╗██╗███████╗
██║  ██║██╔═══██╗██║    ██║    ╚══██╔══╝██╔═══██╗    ██║   ██║██╔════╝██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝██╗
███████║██║   ██║██║ █╗ ██║       ██║   ██║   ██║    ██║   ██║███████╗█████╗         ██║   ███████║██║███████╗╚═╝
██╔══██║██║   ██║██║███╗██║       ██║   ██║   ██║    ██║   ██║╚════██║██╔══╝         ██║   ██╔══██║██║╚════██║██╗
██║  ██║╚██████╔╝╚███╔███╔╝       ██║   ╚██████╔╝    ╚██████╔╝███████║███████╗       ██║   ██║  ██║██║███████║╚═╝
╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝        ╚═╝    ╚═════╝      ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝   

You must create a 'postgresql_sample_config.py' file at this folder with the needed fields (look at the import)
That file will be ignored in git, so do not worry about pushing credentials anywhere (but BE CAREFUL!)
DO NOT REPLACE THIS WITH HARD CODED CREDENTIALS EVER AND ALWAYS REVIEW YOUR COMMITS!
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from longitude.core.caches.ram import RamCache
from longitude.core.data_sources.base import LongitudeRetriesExceeded
from longitude.core.data_sources.postgres.default import DefaultPostgresDataSource
from longitude.samples.postgres_sample_config import POSTGRES_DB, POSTGRES_PORT, POSTGRES_HOST, POSTGRES_USER, \
    POSTGRES_PASS

if __name__ == "__main__":
    config = {
        'host': POSTGRES_HOST or 'localhost',
        'port': POSTGRES_PORT or 5432,
        'db': POSTGRES_DB or 'longitude',
        'user': POSTGRES_USER or 'longitude',
        'password': POSTGRES_PASS or 'longitude'
    }

    ds = DefaultPostgresDataSource(config, cache_class=RamCache)
    ds.setup()
    if ds.is_ready:
        try:

            r0 = ds.query("drop table if exists users", use_cache=False)
            r1 = ds.query(
                'create table users(id serial PRIMARY KEY, name varchar(50) UNIQUE NOT NULL, password varchar(50))',
                needs_commit=True,
                use_cache=False
            )
            print(r1.profiling)

            for i in range(10):
                r2 = ds.query("insert into users(name, password) values(%(user)s, %(password)s)",
                              needs_commit=True,
                              use_cache=False,
                              params={
                                  'user': 'longitude_user_' + str(i),
                                  'password': 'unsafe_password_' + str(i)

                              })
                print(r2.profiling)

            r3 = ds.query('select * from users', use_cache=True)

            print(r3.rows)
            print(r3.profiling)

            r4 = ds.query('select * from users', use_cache=True)
            print(r4.profiling)
            print('It is %f times faster using cache' % (r4.profiling['execute_time'] / r4.profiling['cache_time']))

        except LongitudeRetriesExceeded:
            print("Too many retries and no success...")
    else:
        print("Data source is not properly configured.")
