import redis

from .base import LongitudeCache


class RedisCache(LongitudeCache):
    _default_config = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': None,
        'expiration_time_s': None
    }

    def __init__(self, options={}):
        super().__init__(options)

        self._redis = redis.Redis(
            host=options.get('host', 'localhost'),
            port=options.get('port', 6379),
            db=options.get('db', 0),
            password=options.get('password')
        )
        self.expiration_time = options.get('expiration_time_s')

    def execute_get(self, key):
        return self._redis.get(name=key)

    def execute_put(self, key, payload, expiration_time_s=None):
        overwrite = self._redis.exists(key) == 1
        self._redis.set(name=key, value=payload)
        expiration_time_s = expiration_time_s or self.expiration_time
        if expiration_time_s:
            self._redis.expire(name=key, time=expiration_time_s)
        return overwrite

    def flush(self):
        self._redis.flushall()
