import os
from longitude.core.data_sources.postgres.default import DefaultPostgresDataSource
from longitude.core.data_sources.carto import CartoDataSource
from longitude.core.common.config import EnvironmentConfiguration as Config


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

    carto = CartoDataSource(config='carto_main')
    postgres = DefaultPostgresDataSource(config='postgres_main')

    if carto.is_ready and postgres.is_ready:
        copy_from_sample(carto)
        copy_from_sample(postgres)
