from core.data_sources.base import LongitudeRetriesExceeded
from core.data_sources.carto import CartoDataSource

# This module is IGNORED in git. Create one in your repo and add the needed fields.
# Ask your PM about where to find these values
from core.samples.carto_sample_config import CARTO_API_KEY, CARTO_URL

if __name__ == "__main__":
    config = {
        'api_version': 'v2',
        'uses_batch': False,
        'api_key': CARTO_API_KEY,
        'user_url': CARTO_URL
    }

    ds = CartoDataSource(config)
    ds.setup()
    if ds.is_ready:
        try:
            data = ds.query('select 1 + 1')
            print(data)
        except LongitudeRetriesExceeded:
            print ("caca")
    else:
        print("tararí")
