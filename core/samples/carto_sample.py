"""
██╗  ██╗ ██████╗ ██╗    ██╗    ████████╗ ██████╗     ██╗   ██╗███████╗███████╗    ████████╗██╗  ██╗██╗███████╗
██║  ██║██╔═══██╗██║    ██║    ╚══██╔══╝██╔═══██╗    ██║   ██║██╔════╝██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝██╗
███████║██║   ██║██║ █╗ ██║       ██║   ██║   ██║    ██║   ██║███████╗█████╗         ██║   ███████║██║███████╗╚═╝
██╔══██║██║   ██║██║███╗██║       ██║   ██║   ██║    ██║   ██║╚════██║██╔══╝         ██║   ██╔══██║██║╚════██║██╗
██║  ██║╚██████╔╝╚███╔███╔╝       ██║   ╚██████╔╝    ╚██████╔╝███████║███████╗       ██║   ██║  ██║██║███████║╚═╝
╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝        ╚═╝    ╚═════╝      ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝   

You must create a 'carto_sample_config.py' file at this folder with the needed fields (look at the import)
That file will be ignored in git, so do not worry about pushing credentials anywhere (but BE CAREFUL!)
DO NOT REPLACE THIS WITH HARD CODED CREDENTIALS EVER AND ALWAYS REVIEW YOUR COMMITS!
"""
from core.data_sources.base import LongitudeRetriesExceeded
from core.data_sources.carto import CartoDataSource
from core.samples.carto_sample_config import CARTO_API_KEY, CARTO_USER

if __name__ == "__main__":
    config = {
        'api_key': CARTO_API_KEY,
        'user': CARTO_USER
    }

    ds = CartoDataSource(config)
    ds.setup()
    if ds.is_ready:
        try:
            data = ds.query('select * from county_population limit 30')
            print(data)
        except LongitudeRetriesExceeded:
            print("Too many retries and no success...")
    else:
        print("Data source is not properly configured.")
