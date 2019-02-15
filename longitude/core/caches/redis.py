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

    _values = None

    def __init__(self, config=''):
        super().__init__(config=config)

        self._values = redis.Redis(
            host=self.get_config('host'),
            port=self.get_config('port'),
            db=self.get_config('db'),
            password=self.get_config('password')
        )

    @property
    def is_ready(self):
        try:
            self._values.ping()
            return True
        except TimeoutError:
            return False
        except redis.exceptions.ConnectionError:
            self.logger.error(
                'Cannot connect to Redis server at %s:%d.' % (self.get_config('host'), self.get_config('port')))
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

    def execute_put(self, key, payload, expiration_time_s=None):
        overwrite = self._values.exists(key) == 1
        self._values.set(name=key, value=payload)
        expiration_time_s = expiration_time_s or self.get_config('expiration_time_s')
        if expiration_time_s:
            self._values.expire(name=key, time=expiration_time_s)
        return overwrite

    def flush(self):
        self._values.flushall()
