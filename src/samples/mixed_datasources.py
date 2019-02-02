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

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.caches.redis import RedisCache
from src.core.data_sources.postgres.default import DefaultPostgresDataSource
from src.core.data_sources.carto import CartoDataSource
from src.core.common.config import EnvironmentConfiguration


def import_table_values_from_carto(limit):
    # First, we read from CARTO our 'county_population'
    carto_data = carto.query('select * from county_population limit %d' % limit, use_cache=True)

    # Then, we create a local table
    postgres.query("drop table if exists county_population", use_cache=False)
    postgres.query(
        'create table county_population(id serial PRIMARY KEY, cartodb_id integer UNIQUE NOT NULL, the_geom text)',
        needs_commit=True,
        use_cache=False
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


if __name__ == "__main__":

    # This is the global config object
    # We are going to retrieve some values from a table in Carto, create a local table and copy the values
    # doing simple inserts (to show how to do queries)

    config = EnvironmentConfiguration({
        'carto_main': {
            'api_key': "=CARTO_API_KEY",
            'user': "=CARTO_USER",

            'cache': {
                'password': '=REDIS_PASSWORD'
            }
        },
        'postgres_main': {
            'host': "=POSTGRES_HOST",
            'port': "=POSTGRES_PORT",
            'db': "=POSTGRES_DB",
            'user': "=POSTGRES_USER",
            'password': "=POSTGRES_PASS"
        }
    })

    carto = CartoDataSource(config['carto_main'], cache_class=RedisCache)
    postgres = DefaultPostgresDataSource(config['postgres_main'])
    carto.setup()
    postgres.setup()

    if carto.is_ready and postgres.is_ready():
        import_table_values_from_carto(limit=30)
