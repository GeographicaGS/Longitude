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

from longitude.core.data_sources.carto import CartoDataSource  # noqa
from longitude.samples.config import config  # noqa


if __name__ == "__main__":

    ds = CartoDataSource(
        user=config['carto_user'],
        api_key=config['carto_api_key']
    )

    data = ds.query('select * from country_population limit 30')
    [print(r) for r in data.rows]
    print(data.meta)

    # Pandas DataFrame read/write
    # ########################################
    df = ds.read_dataframe(table_name='country_population', limit=30)
    print(df)
    ds.write_dataframe(df=df, table_name='temp_debug_delete_me', overwrite=True)
