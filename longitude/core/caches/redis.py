import redis
from aredis import StrictRedis

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
        self._options = options

        self._async_redis_client = None
        self._redis_client = None
        self.expiration_time = options.get('expiration_time_s')

    @property
    def _redis(self):
        # Lazy initialization of the syncronous redis client
        if not self._redis_client:
            self._redis_client = redis.Redis(
                host=self._options.get('host', 'localhost'),
                port=self._options.get('port', 6379),
                db=self._options.get('db', 0),
                password=self._options.get('password')
            )
        return self._redis_client

    @property
    def _aredis(self):
        # Lazy initialization of the async redis client
        if not self._async_redis_client:
            self._async_redis_client = StrictRedis(
                host=self._options.get('host', 'localhost'),
                port=self._options.get('port', 6379),
                db=self._options.get('db', 0),
                password=self._options.get('password')
            )
        return self._async_redis_client

    def execute_get(self, key):
        return self._redis.get(name=key)

    async def execute_get_async(self, key):
        return await self._aredis.get(name=key)

    def execute_put(self, key, payload, expiration_time_s=None):
        overwrite = self._redis.exists(key) == 1

        opt = {}
        expiration_time_s = expiration_time_s or self.expiration_time
        if expiration_time_s:
            opt['ex'] = expiration_time_s

        self._redis.set(name=key, value=payload, **opt)
        return overwrite

    async def execute_put_async(self, key, payload, expiration_time_s=None):
        overwrite = await self._aredis.exists(key) == 1

        opt = {}
        expiration_time_s = expiration_time_s or self.expiration_time
        if expiration_time_s:
            opt['ex'] = expiration_time_s

        await self._aredis.set(name=key, value=payload, **opt)
        return overwrite

    def flush(self):
        self._redis.flushall()

    def flush_async(self):
        self._aredis.flushall()
