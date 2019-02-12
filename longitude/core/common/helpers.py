import inspect

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


def method_not_supported(o):
    # We assume that this function is called from an object (o) directly from the not supported method
    # If so, the index 1 in the stack is the call previous to method_not_supported, so it holds the info about the
    # previous call (the not supported method!). Then we take the name, which is stored in the third index.
    method = inspect.stack()[1][3]

    o.logger.error("%s does not support %s" % (o.__class__.__name__, method))
