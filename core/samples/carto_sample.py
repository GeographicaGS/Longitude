from core.data_sources.base import LongitudeRetriesExceeded
from core.data_sources.carto import CartoDataSource

# This module is IGNORED in git. Create one in your repo and add the needed fields.
# Ask your PM about where to find these values
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
