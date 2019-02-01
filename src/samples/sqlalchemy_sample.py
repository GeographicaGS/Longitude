"""
██╗  ██╗ ██████╗ ██╗    ██╗    ████████╗ ██████╗     ██╗   ██╗███████╗███████╗    ████████╗██╗  ██╗██╗███████╗
██║  ██║██╔═══██╗██║    ██║    ╚══██╔══╝██╔═══██╗    ██║   ██║██╔════╝██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝██╗
███████║██║   ██║██║ █╗ ██║       ██║   ██║   ██║    ██║   ██║███████╗█████╗         ██║   ███████║██║███████╗╚═╝
██╔══██║██║   ██║██║███╗██║       ██║   ██║   ██║    ██║   ██║╚════██║██╔══╝         ██║   ██╔══██║██║╚════██║██╗
██║  ██║╚██████╔╝╚███╔███╔╝       ██║   ╚██████╔╝    ╚██████╔╝███████║███████╗       ██║   ██║  ██║██║███████║╚═╝
╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝        ╚═╝    ╚═════╝      ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝   

You must create a 'sqlalchemy_sample_config.py' file at this folder with the needed fields (look at the import)
That file will be ignored in git, so do not worry about pushing credentials anywhere (but BE CAREFUL!)
DO NOT REPLACE THIS WITH HARD CODED CREDENTIALS EVER AND ALWAYS REVIEW YOUR COMMITS!
"""
import os
import sys

from sqlalchemy import text

from src.core.caches.ram import RamCache

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core.data_sources.postgres.sqlalchemy import SQLAlchemyDataSource
from src.samples.sqlalchemy_sample_config import POSTGRES_DB, POSTGRES_PORT, POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASS


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
    config = {
        'host': POSTGRES_HOST or 'localhost',
        'port': POSTGRES_PORT or 5432,
        'db': POSTGRES_DB or 'longitude',
        'user': POSTGRES_USER or 'longitude',
        'password': POSTGRES_PASS or 'longitude'
    }

    ds = SQLAlchemyDataSource(config, cache_class=RamCache)
    ds.setup()
    if ds.is_ready:
        # We prepare a table to play around
        table = prepare_sample_table(ds._engine)

        # Demo insert. Notice how values are passed as parameters instead of just pasted into some string
        q = table.insert()
        params = [
            {'name': 'tony', 'fullname': 'Tony Stark Jr.', 'password': 'smartestavenger'},
            {'name': 'hulk', 'fullname': 'Dr. Phd. Bruce Banner', 'password': 'smartestavenger'},
            {'name': 'cap', 'fullname': 'Capt. Steve Rogers', 'password': 'igotthatreference'}
        ]
        ds.query(q, params, use_cache=False)

        # Demo select. Again, the search is done by a parametrized query. In this case, direct text is used as
        #  where clause.
        q = table.select('password = :password')
        params = {'password': 'igotthatreference'}
        r = ds.query(q, params, use_cache=True)
        print(r.fields)
        print(r.rows)
        print("Cached? " + str(r.comes_from_cache))

        # Just repeat to check the cache working
        r = ds.query(q, params, use_cache=True)
        print(r.rows)
        print("Cached? " + str(r.comes_from_cache))
    else:
        print("Data source is not properly configured.")
