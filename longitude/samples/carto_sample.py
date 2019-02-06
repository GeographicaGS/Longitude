"""
██╗  ██╗ ██████╗ ██╗    ██╗    ████████╗ ██████╗     ██╗   ██╗███████╗███████╗    ████████╗██╗  ██╗██╗███████╗
██║  ██║██╔═══██╗██║    ██║    ╚══██╔══╝██╔═══██╗    ██║   ██║██╔════╝██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝██╗
███████║██║   ██║██║ █╗ ██║       ██║   ██║   ██║    ██║   ██║███████╗█████╗         ██║   ███████║██║███████╗╚═╝
██╔══██║██║   ██║██║███╗██║       ██║   ██║   ██║    ██║   ██║╚════██║██╔══╝         ██║   ██╔══██║██║╚════██║██╗
██║  ██║╚██████╔╝╚███╔███╔╝       ██║   ╚██████╔╝    ╚██████╔╝███████║███████╗       ██║   ██║  ██║██║███████║╚═╝
╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝        ╚═╝    ╚═════╝      ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝   

You must create a 'carto_sample_config.py' file at this folder with the needed fields (look at the import)
   !!! As dataframe write is an IMPORT API operation, only the master api key will work !!!

That file will be ignored in git, so do not worry about pushing credentials anywhere (but BE CAREFUL!)
DO NOT REPLACE THIS WITH HARD CODED CREDENTIALS EVER AND ALWAYS REVIEW YOUR COMMITS!
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from longitude.core.data_sources.base import LongitudeRetriesExceeded
from longitude.core.data_sources.carto import CartoDataSource
from longitude.samples.carto_sample_config import CARTO_API_KEY, CARTO_USER, CARTO_TABLE_NAME

import pandas as pd

if __name__ == "__main__":
    config = {
        'api_key': CARTO_API_KEY,
        'user': CARTO_USER
    }

    ds = CartoDataSource(config)
    ds.setup()
    if ds.is_ready:
        try:

            # SQL API Call using regular SQL statement
            # ########################################
            data = ds.query('select * from %s limit 30' % CARTO_TABLE_NAME)
            [print(r) for r in data.rows]
            print(data.profiling)

            # Pandas DataFrame read/write
            # ########################################
            df = ds.cc.read(table_name=CARTO_TABLE_NAME, limit=30)
            print(df)
            ds.cc.write(df=df, table_name='another_county_population', overwrite=True)


        except LongitudeRetriesExceeded:
            print("Too many retries and no success...")
    else:
        print("Data source is not properly configured.")
