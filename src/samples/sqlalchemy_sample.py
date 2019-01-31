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

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core.data_sources.base import LongitudeRetriesExceeded
from src.core.data_sources.postgres.sqlalchemy import SQLAlchemyDataSource
from src.samples.sqlalchemy_sample_config import POSTGRES_DB, POSTGRES_PORT, POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASS

from sqlalchemy import Column, Integer, String

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

        class User(ds.base_class):
            __tablename__ = 'users'

            id = Column(Integer, primary_key=True)
            name = Column(String)
            fullname = Column(String)
            password = Column(String)

            def __repr__(self):
                return "<User(name='%s', fullname='%s', password='%s')>" % (self.name, self.fullname, self.password)


        ds.create_all()
    else:
        print("Data source is not properly configured.")
