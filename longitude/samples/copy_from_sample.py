import os
from longitude.core.data_sources.postgres.default import PostgresDataSource
from longitude.core.data_sources.carto import CartoDataSource

from longitude.samples.config import config


def copy_from_sample(ds):
    # Copy from csv
    # ########################################
    to_table = 'avengers_names'
    ds.query('DROP TABLE IF EXISTS %s' % to_table)
    ds.query('CREATE TABLE %s (id serial PRIMARY KEY, name text, color text)' % to_table, needs_commit=True)
    filepath = os.path.join(os.path.dirname(__file__), 'demo_data.csv')
    r = ds.copy_from_csv(csv_file_absolute_path=filepath, to_table=to_table)
    print('Response from copy operation: %s' % str(r))
    r = ds.query("SELECT name FROM " + to_table + " WHERE color=%(color)s", params={'color': 'green'})
    [print(row.get('name')) for row in r.rows]


if __name__ == "__main__":

    carto = CartoDataSource(user=config['carto_user'], api_key=config['carto_api_key'])
    postgres = PostgresDataSource({
        'user': config['pg_user'],
        'password': config['pg_password']
    })

    copy_from_sample(carto)
    copy_from_sample(postgres)
