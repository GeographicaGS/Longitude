import redis.exceptions
from unittest import TestCase, mock
from ..caches.redis import RedisCache


@mock.patch('src.core.caches.redis.redis.Redis')
class TestRedisCache(TestCase):
    cache = None

    def setUp(self):
        test_config = {
            'host': 'some_host',
            'port': 666,
            'db': 0
        }
        self.cache = RedisCache(config=test_config)

    def test_is_ready_if_redis_returns_ping(self, redis_mock):
        redis_mock.return_value.ping.return_value = True
        self.cache.setup()
        self.assertTrue(self.cache.is_ready)

        redis_mock.return_value.get.return_value = None
        self.assertIsNone(self.cache.get('fake_key'))
        redis_mock.return_value.get.assert_called_once()

        redis_mock.return_value.set.return_value = None
        self.assertFalse(self.cache.put('some_key', 'some_payload'))
        redis_mock.return_value.exists.return_value = 1
        self.assertTrue(self.cache.put('some_key', 'some_payload'))
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
                'ERROR:src.core.caches.redis:Cannot connect to Redis server at some_host:666.'
            ]

            self.assertEqual(expected_log, log_test.output)

    def test_is_not_ready_if_redis_fails_ping_because_of_timeout(self, redis_mock):
        redis_mock.return_value.ping.side_effect = TimeoutError
        self.cache.setup()
        self.assertFalse(self.cache.is_ready)
