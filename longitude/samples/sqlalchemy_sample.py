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

from longitude.core.data_sources.postgres.sqlalchemy import SQLAlchemyDataSource  # noqa
from longitude.samples.config import config  # noqa


def prepare_sample_table(engine):
    """ This is just one way to provide table to show how queries work.
        You can generate your queries as you prefer by using any of the SQL Alchemy APIs
    """

    class Avenger(ds.base_class):
        from sqlalchemy import Column, Integer, String
        __tablename__ = 'avengers'

        id = Column(Integer, primary_key=True)
        name = Column(String)
        fullname = Column(String)
        password = Column(String)

        def __repr__(self):
            return "<Avenger(name='%s', fullname='%s', password='%s')>" % (self.name, self.fullname, self.password)

    if Avenger.__table__.exists(engine):
        Avenger.__table__.drop(engine)
    Avenger.__table__.create(engine)
    return Avenger.__table__


if __name__ == "__main__":
    options = {
        'user': config['pg_user'],
        'password': config['pg_password']
    }

    ds = SQLAlchemyDataSource(options)

    # We prepare a table to play around
    table = prepare_sample_table(ds._engine)

    # Demo insert. Notice how values are passed as parameters instead of just pasted into some string
    q = table.insert()

    # With SQLAlchemy we can bind lists and subsequent rendered queries will be executed
    params = [
        {'name': 'tony', 'fullname': 'Tony Stark Jr.', 'password': 'smartestavenger'},
        {'name': 'hulk', 'fullname': 'Dr. Phd. Bruce Banner', 'password': 'smartestavenger'},
        {'name': 'cap', 'fullname': 'Capt. Steve Rogers', 'password': 'igotthatreference'}
    ]
    ds.query(q, params, cache=False)

    # Demo select. Again, the search is done by a parametrized query. In this case, direct text is used as
    #  where clause.
    q = table.select('password = :password')
    params = {'password': 'igotthatreference'}
    r = ds.query(q, params, cache=True)
    print(r.fields)
    print(r.rows)
    print("Cached? " + str(r.from_cache))

    # Just repeat to check the cache working
    r = ds.query(q, params, cache=True)
    print(r.rows)
    print("Cached? " + str(r.from_cache))

    # Work with data as dataframes

    ds.query('DROP TABLE IF EXISTS new_avengers')
    ds.query('DROP TABLE IF EXISTS green_avengers')

    df = ds.read_dataframe(table_name='avengers')
    ds.write_dataframe(df, table_name='new_avengers')
    df = ds.query_dataframe(query="SELECT * FROM avengers where name='hulk'")
    ds.write_dataframe(df, table_name='green_avengers')

    r = ds.query('SELECT * FROM green_avengers')
    print(r.rows[0])
