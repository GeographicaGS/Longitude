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

    ds = SQLAlchemyDataSource(config)
    ds.setup()
    if ds.is_ready:
        table = prepare_sample_table(ds._engine)
        q = table.insert()
        params = [
            {'name': 'tony', 'fullname': 'Tony Stark Jr.', 'password': 'smartestavenger'},
            {'name': 'hulk', 'fullname': 'Dr. Phd. Bruce Banner', 'password': 'smartestavenger'},
            {'name': 'cap', 'fullname': 'Capt. Steve Rogers', 'password': 'igotthatreference'}
        ]
        ds.query(q, params, use_cache=False)
        q = table.select('password = :password')
        params = {'password': 'igotthatreference'}
        r = ds.query(q, params)
        print(r)
    else:
        print("Data source is not properly configured.")
