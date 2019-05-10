from unittest import TestCase, mock

from longitude.core.common.query_response import LongitudeQueryResponse

from ..caches.redis import RedisCache

TESTED_MODULE_PATH = 'longitude.core.caches.redis.%s'


class TestRedisCache(TestCase):
    cache = None

    def setUp(self):
        patcher = mock.patch(TESTED_MODULE_PATH % 'redis.Redis')
        self.addCleanup(patcher.stop)
        self.redis_mock = patcher.start()

        self.cache = RedisCache()

    def test_if_redis_returns_ping(self):
        self.redis_mock.return_value.ping.return_value = True

        self.redis_mock.return_value.get.return_value = None
        self.assertIsNone(self.cache.get('fake_key'))
        self.redis_mock.return_value.get.assert_called_once()

        self.redis_mock.return_value.set.return_value = None
        self.assertFalse(self.cache.put('some_key', LongitudeQueryResponse()))
        self.redis_mock.return_value.exists.return_value = 1
        self.assertTrue(self.cache.put('some_key', LongitudeQueryResponse()))
        self.assertEqual(2, self.redis_mock.return_value.set.call_count)

        self.redis_mock.return_value.flushall.return_value = None
        self.cache.flush()
        self.redis_mock.return_value.flushall.assert_called_once()

    def test_is_not_ready_if_redis_fails_ping_because_of_timeout(self):
        self.redis_mock.return_value.ping.side_effect = TimeoutError
