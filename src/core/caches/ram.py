from .base import LongitudeCache


class RamCache(LongitudeCache):
    """
    This is the simplest cache we can use: a dictionary in memory.
    """
    _values = {}

    def setup(self):
        self.flush()

    @property
    def is_ready(self):
        return True

    def execute_get(self, key):
        return self._values.get(key)

    def execute_put(self, key, payload):
        is_overwrite = key in self._values.keys()
        self._values[key] = payload
        return is_overwrite

    def flush(self):
        self._values = {}

    @staticmethod
    def serialize_payload(payload):
        return payload

    @staticmethod
    def deserialize_payload(payload):
        return payload
