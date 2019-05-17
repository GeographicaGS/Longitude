from .base import LongitudeCache


class RamCache(LongitudeCache):
    """
    This is the simplest cache we can use: a dictionary in memory.
    """
    _values = {}

    def execute_get(self, key):
        return self._values.get(key)

    async def execute_get_async(self, key):
        return self.execute_get(key)

    def execute_put(self, key, payload, expiration_time_s=None):
        if expiration_time_s:
            self.logger.warning("RamCache does not support expiration time. Ignoring configuration.")
        is_overwrite = key in self._values.keys()
        self._values[key] = payload
        return is_overwrite

    async def execute_put_async(self, key, payload, expiration_time_s=None):
        return self.execute_put(key, payload, expiration_time_s=None)

    def flush(self):
        self._values = {}

    async def flush_async(self):
        self.flush()

    @staticmethod
    def serialize_payload(payload):
        return payload

    @staticmethod
    def deserialize_payload(payload):
        return payload
