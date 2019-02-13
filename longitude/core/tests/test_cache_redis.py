from unittest import TestCase, mock

import redis.exceptions

from longitude.core.common.query_response import LongitudeQueryResponse

from ..caches.redis import RedisCache

TESTED_MODULE_PATH = 'longitude.core.caches.redis.%s'


class TestRedisCache(TestCase):
    cache = None

    def setUp(self):
        patcher = mock.patch(TESTED_MODULE_PATH % 'redis.Redis')
        self.addCleanup(patcher.stop)
        self.redis_mock = patcher.start()

        self.cache = RedisCache(name='test_cache')

    def test_is_ready_if_redis_returns_ping(self):
        self.redis_mock.return_value.ping.return_value = True
        self.assertTrue(self.cache.is_ready)

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

    def test_is_not_ready_if_redis_fails_ping_because_of_connection_error(self):
        self.redis_mock.return_value.ping.side_effect = redis.exceptions.ConnectionError

        with self.assertLogs(level='ERROR') as log_test:
            self.assertFalse(self.cache.is_ready)
            expected_log = [
                'ERROR:longitude.core.caches.redis:Cannot connect to Redis server at localhost:6379.'
            ]

            self.assertEqual(expected_log, log_test.output)

    def test_is_not_ready_if_redis_fails_ping_because_of_timeout(self):
        self.redis_mock.return_value.ping.side_effect = TimeoutError
        self.assertFalse(self.cache.is_ready)

    def test_is_not_ready_because_no_password(self):
        self.redis_mock.return_value.ping.side_effect = redis.exceptions.ResponseError(
            'NOAUTH Authentication required.')
        with self.assertLogs(level='ERROR') as log_test:
            self.assertFalse(self.cache.is_ready)
            self.assertEqual(['ERROR:longitude.core.caches.redis:Redis password required.'], log_test.output)

    def test_is_not_ready_because_wrong_password(self):
        self.redis_mock.return_value.ping.side_effect = redis.exceptions.ResponseError('invalid password')
        with self.assertLogs(level='ERROR') as log_test:
            self.assertFalse(self.cache.is_ready)
            self.assertEqual(['ERROR:longitude.core.caches.redis:Redis password is wrong.'], log_test.output)

    def test_is_not_ready_because_of_generic_response_error(self):
        self.redis_mock.return_value.ping.side_effect = redis.exceptions.ResponseError('some error text')
        with self.assertLogs(level='ERROR') as log_test:
            self.assertFalse(self.cache.is_ready)
            self.assertEqual(['ERROR:longitude.core.caches.redis:some error text'], log_test.output)
