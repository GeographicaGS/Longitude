from longitude.core.data_sources.base import DataSource


class DisabledCache:
    data_source = None

    def __init__(self, ds):
        if ds and not isinstance(ds, DataSource):
            raise TypeError('DisabledCache can only be applied to DataSource subclasses.')
        self.data_source = ds

    def __enter__(self):
        self.data_source.disable_cache()

    def __exit__(self, *args):
        self.data_source.enable_cache()
