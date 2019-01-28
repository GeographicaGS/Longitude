import redis
from .base import LongitudeCache


class RedisCache(LongitudeCache):
    default_config = {
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }

    _values = None

    def setup(self):
        self._values = redis.Redis(host=self._config['host'], port=self._config['port'], db=self._config['db'])

    @property
    def is_ready(self):
        try:
            self._values.ping()
            return True
        except TimeoutError:
            return False
        except redis.exceptions.ConnectionError as e:
            self.logger.error('Cannot connect to Redis server at %s:%d.' % (self._config['host'], self._config['port']))
            return False

    def execute_get(self, key):
        return self._values.get(name=key)

    def execute_put(self, key, payload):
        overwrite = self._values.exists(key) == 1
        self._values.set(name=key, value=payload)
        return overwrite

    def flush(self):
        self._values.flushall()
