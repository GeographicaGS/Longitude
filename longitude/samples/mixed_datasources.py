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

from longitude.core.data_sources.postgres.default import PostgresDataSource  # noqa
from longitude.core.data_sources.carto import CartoDataSource  # noqa
from longitude.samples.config import config  # noqa


def run_query(ds):
    data = ds.query('select * from country_population limit 30')

    return data


if __name__ == "__main__":

    carto = CartoDataSource(
        user=config['carto_user'],
        api_key=config['carto_api_key']
    )
    postgres = PostgresDataSource({'user': 'user', 'password': 'userpass'})

    carto_data = run_query(carto)
    print(carto_data.meta)
    print('------ \n')

    pg_data = run_query(postgres)
    # Notice that there is no meta-data for postgres results
    print(pg_data.meta)
    [print(r) for r in pg_data.rows[:1]]

    # ... nice
