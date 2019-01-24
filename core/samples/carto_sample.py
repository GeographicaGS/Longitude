import os
from core.data_sources.carto import CartoDataSource

if __name__ == "__main__":
    config = {
        'api_version': 'v2',
        'uses_batch': False,
        'api_key': os.environ('SAMPLE_CARTO_API_KEY'),
        'user_url': os.environ('SAMPLE_CARTO_USER_URL')
    }

    ds = CartoDataSource(config)
