"""
██╗  ██╗ ██████╗ ██╗    ██╗    ████████╗ ██████╗     ██╗   ██╗███████╗███████╗    ████████╗██╗  ██╗██╗███████╗
██║  ██║██╔═══██╗██║    ██║    ╚══██╔══╝██╔═══██╗    ██║   ██║██╔════╝██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝██╗
███████║██║   ██║██║ █╗ ██║       ██║   ██║   ██║    ██║   ██║███████╗█████╗         ██║   ███████║██║███████╗╚═╝
██╔══██║██║   ██║██║███╗██║       ██║   ██║   ██║    ██║   ██║╚════██║██╔══╝         ██║   ██╔══██║██║╚════██║██╗
██║  ██║╚██████╔╝╚███╔███╔╝       ██║   ╚██████╔╝    ╚██████╔╝███████║███████╗       ██║   ██║  ██║██║███████║╚═╝
╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝        ╚═╝    ╚═════╝      ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝

You must create the environment variables needed and the county_population in your Carto account.
(We just use the cartodb_id field, so it does not matter what you put there)
This is an example that you can run using the provided docker-compose configuration.

A fast method is:

1. copy .env.sample -> .env
2. edit .env adding the carto credentials and table
3. (re)activate your pipenv shell; it will load the variables in that shell

We are focusing here on the configuration process so there is no error flow control nor fancy query construction.
For such features, check specific samples.

"""
import os
import sys

from environs import Env

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from longitude.core.data_sources.postgres.default import PostgresDataSource
from longitude.core.data_sources.carto import CartoDataSource


def import_table_values_from_carto(limit):
    # First, we read from CARTO our 'county_population'
    # If you execute this script twice fast, you will make use of the cache.
    # After 3 seconds, the Carto query will be executed again if requested.
    carto_data = carto.query('select * from county_population limit %d' % limit, cache=True, expiration_time_s=3)
    print(carto_data.from_cache)
    # Then, we create a local table
    postgres.query("drop table if exists county_population", cache=False)
    postgres.query(
        'create table county_population(id serial PRIMARY KEY, cartodb_id integer UNIQUE NOT NULL, the_geom text)',
        needs_commit=True,
        cache=False
    )

    # Now we want to copy row by row these values using simple inserts:

    # Using psycopg2 directly, we must build our queries and parameters carefully
    # i.e. when doing multiple values inserts:
    values_template = ('(%s,%s),' * limit)[:-1]
    params = [None] * limit * 2  # We reserve places for all values (=limit) for all columns (=2)...
    params[::2] = [r['cartodb_id'] for r in carto_data.rows]  # ... and we alternate id and geom in the values
    params[1::2] = [r['the_geom'] for r in carto_data.rows]  # This way is both efficient (not using copy) and safe

    postgres.query(
        'insert into county_population (cartodb_id, the_geom) values %s' % values_template,
        params=params,
        needs_commit=True)

    res = postgres.query('select * from county_population')
    print(res.rows)


if __name__ == "__main__":

    # Getting needed env configs:
    env = Env()
    user = env('CARTO_USER')
    api_key = env('CARTO_API_KEY')

    carto = CartoDataSource(user=user, api_key=api_key)
    postgres = PostgresDataSource({'user': 'user', 'password': 'userpass'})
    # No exceptions.. both connections ok...