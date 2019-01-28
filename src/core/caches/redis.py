import redis
from .base import LongitudeCache


class RedisCacheConfig:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password


class RedisCache(LongitudeCache):
    _default_config = RedisCacheConfig()

    _values = None

    def setup(self):
        self._values = redis.Redis(
            host=self._config.host,
            port=self._config.port,
            db=self._config.db,
            password=self._config.password
        )

    @property
    def is_ready(self):
        try:
            self._values.ping()
            return True
        except TimeoutError:
            return False
        except redis.exceptions.ConnectionError:
            self.logger.error('Cannot connect to Redis server at %s:%d.' % (self._config.host, self._config.port))
            return False
        except redis.exceptions.ResponseError as e:
            msg = str(e)
            if str(e) == 'invalid password':
                msg = 'Redis password is wrong.'
            elif str(e) == "NOAUTH Authentication required.":
                msg = 'Redis password required.'
            self.logger.error(msg)
            return False

    def execute_get(self, key):
        return self._values.get(name=key)

    def execute_put(self, key, payload):
        overwrite = self._values.exists(key) == 1
        self._values.set(name=key, value=payload)
        return overwrite

    def flush(self):
        self._values.flushall()
