"""
██╗  ██╗ ██████╗ ██╗    ██╗    ████████╗ ██████╗     ██╗   ██╗███████╗███████╗    ████████╗██╗  ██╗██╗███████╗
██║  ██║██╔═══██╗██║    ██║    ╚══██╔══╝██╔═══██╗    ██║   ██║██╔════╝██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝██╗
███████║██║   ██║██║ █╗ ██║       ██║   ██║   ██║    ██║   ██║███████╗█████╗         ██║   ███████║██║███████╗╚═╝
██╔══██║██║   ██║██║███╗██║       ██║   ██║   ██║    ██║   ██║╚════██║██╔══╝         ██║   ██╔══██║██║╚════██║██╗
██║  ██║╚██████╔╝╚███╔███╔╝       ██║   ╚██████╔╝    ╚██████╔╝███████║███████╗       ██║   ██║  ██║██║███████║╚═╝
╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝        ╚═╝    ╚═════╝      ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝   

Fill the needed environment variables using LONGITUDE__ as prefix!
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from longitude.core.caches.ram import RamCache
from longitude.core.data_sources.base import LongitudeRetriesExceeded
from longitude.core.data_sources.postgres.default import DefaultPostgresDataSource


if __name__ == "__main__":
    ds = DefaultPostgresDataSource(config='postgres_main', cache_class=RamCache)
    if ds.is_ready:
        try:

            r0 = ds.query("drop table if exists users", cache=False)
            r1 = ds.query(
                'create table users(id serial PRIMARY KEY, name varchar(50) UNIQUE NOT NULL, password varchar(50))',
                needs_commit=True,
                cache=False
            )
            print(r1.profiling)

            for i in range(10):
                r2 = ds.query("insert into users(name, password) values(%(user)s, %(password)s)",
                              needs_commit=True,
                              cache=False,
                              params={
                                  'user': 'longitude_user_' + str(i),
                                  'password': 'unsafe_password_' + str(i)

                              })
                print(r2.profiling)

            r3 = ds.query('select * from users', cache=True)

            print(r3.rows)
            print(r3.profiling)

            r4 = ds.query('select * from users', cache=True)
            print(r4.profiling)
            print('It is %f times faster using cache' % (r4.profiling['execute_time'] / r4.profiling['cache_time']))

        except LongitudeRetriesExceeded:
            print("Too many retries and no success...")
    else:
        print("Data source is not properly configured.")
