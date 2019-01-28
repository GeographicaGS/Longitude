import redis
import pickle
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
        except (ConnectionError, TimeoutError):
            return False
        except redis.exceptions.ConnectionError as e:
            self.logger.error('Cannot connect to Redis server.')
            self.logger.error(e)
            return False

    def execute_get(self, key):
        value = self._values.get(name=key)
        if value:
            return pickle.loads(value)
        return None

    def execute_put(self, key, payload):
        self._values.set(name=key, value=pickle.dumps(payload))
