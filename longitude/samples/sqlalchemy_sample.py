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

from longitude.core.caches.ram import RamCache

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from longitude.core.data_sources.postgres.sqlalchemy import SQLAlchemyDataSource


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
    ds = SQLAlchemyDataSource(name='postgres_main', cache_class=RamCache)
    ds.setup()
    if ds.is_ready:
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
