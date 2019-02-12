from unittest import TestCase, mock

import redis.exceptions

from longitude.core.common.query_response import LongitudeQueryResponse

from ..caches.redis import RedisCache


@mock.patch('longitude.core.caches.redis.redis.Redis')
class TestRedisCache(TestCase):
    cache = None

    def setUp(self):
        self.cache = RedisCache(name='test_cache')

    def test_is_ready_if_redis_returns_ping(self, redis_mock):
        redis_mock.return_value.ping.return_value = True
        self.cache.setup()
        self.assertTrue(self.cache.is_ready)

        redis_mock.return_value.get.return_value = None
        self.assertIsNone(self.cache.get('fake_key'))
        redis_mock.return_value.get.assert_called_once()

        redis_mock.return_value.set.return_value = None
        self.assertFalse(self.cache.put('some_key', LongitudeQueryResponse()))
        redis_mock.return_value.exists.return_value = 1
        self.assertTrue(self.cache.put('some_key', LongitudeQueryResponse()))
        self.assertEqual(2, redis_mock.return_value.set.call_count)

        redis_mock.return_value.flushall.return_value = None
        self.cache.flush()
        redis_mock.return_value.flushall.assert_called_once()

    def test_is_not_ready_if_redis_fails_ping_because_of_connection_error(self, redis_mock):
        redis_mock.return_value.ping.side_effect = redis.exceptions.ConnectionError
        self.cache.setup()

        with self.assertLogs(level='ERROR') as log_test:
            self.assertFalse(self.cache.is_ready)
            expected_log = [
                'ERROR:longitude.core.caches.redis:Cannot connect to Redis server at localhost:6379.'
            ]

            self.assertEqual(expected_log, log_test.output)

    def test_is_not_ready_if_redis_fails_ping_because_of_timeout(self, redis_mock):
        redis_mock.return_value.ping.side_effect = TimeoutError
        self.cache.setup()
        self.assertFalse(self.cache.is_ready)

    def test_is_not_ready_because_no_password(self, redis_mock):
        redis_mock.return_value.ping.side_effect = redis.exceptions.ResponseError('NOAUTH Authentication required.')
        self.cache.setup()
        with self.assertLogs(level='ERROR') as log_test:
            self.assertFalse(self.cache.is_ready)
            self.assertEqual(['ERROR:longitude.core.caches.redis:Redis password required.'], log_test.output)

    def test_is_not_ready_because_wrong_password(self, redis_mock):
        redis_mock.return_value.ping.side_effect = redis.exceptions.ResponseError('invalid password')
        self.cache.setup()
        with self.assertLogs(level='ERROR') as log_test:
            self.assertFalse(self.cache.is_ready)
            self.assertEqual(['ERROR:longitude.core.caches.redis:Redis password is wrong.'], log_test.output)

    def test_is_not_ready_because_of_generic_response_error(self, redis_mock):
        redis_mock.return_value.ping.side_effect = redis.exceptions.ResponseError('some error text')
        self.cache.setup()
        with self.assertLogs(level='ERROR') as log_test:
            self.assertFalse(self.cache.is_ready)
            self.assertEqual(['ERROR:longitude.core.caches.redis:some error text'], log_test.output)
