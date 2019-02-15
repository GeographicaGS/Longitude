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

from longitude.core.common.exceptions import LongitudeRetriesExceeded

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from longitude.core.data_sources.carto import CartoDataSource

if __name__ == "__main__":

    ds = CartoDataSource(config='carto_main')

    if ds.is_ready:
        try:
            data = ds.query('select * from county_population limit 30')
            [print(r) for r in data.rows]
            print(data.profiling)

            # Pandas DataFrame read/write
            # ########################################
            df = ds.read_dataframe(table_name='county_population', limit=30)
            print(df)
            ds.write_dataframe(df=df, table_name='another_county_population', overwrite=True)

        except LongitudeRetriesExceeded:
            print("Too many retries and no success...")
    else:
        print("Data source is not properly configured.")
