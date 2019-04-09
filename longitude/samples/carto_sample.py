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

from environs import Env

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from longitude.core.data_sources.carto import CartoDataSource

if __name__ == "__main__":

    # Getting needed env configs:
    env = Env()

    user = env('CARTO_USER')
    api_key = env('CARTO_API_KEY')

    ds = CartoDataSource(user=user, api_key=api_key)

    data = ds.query('select * from county_population limit 30')
    [print(r) for r in data.rows]
    print(data.meta)

    # Pandas DataFrame read/write
    # ########################################
    df = ds.read_dataframe(table_name='county_population', limit=30)
    print(df)
    ds.write_dataframe(df=df, table_name='temp_debug_delete_me', overwrite=True)
