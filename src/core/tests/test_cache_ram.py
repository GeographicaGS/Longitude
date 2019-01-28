from unittest import TestCase, mock
from ..caches.ram import RamCache


class TestRedisCache(TestCase):
    cache = None

    def setUp(self):
        self.cache = RamCache()

    def test_setup_must_clean_cache(self):
        with mock.patch('src.core.caches.ram.RamCache.flush') as fake_flush:
            self.cache.setup()
            fake_flush.assert_called_once()
        self.assertTrue(self.cache.is_ready)

    def test_serialization_does_nothing(self):
        self.assertEqual('value', self.cache.serialize_payload('value'))
        self.assertEqual('value', self.cache.deserialize_payload('value'))

    def test_read_write_flush_cycle(self):
        self.assertIsNone(self.cache.get('fake_key'))
        self.assertFalse(self.cache.put('key', 'value'))
        self.assertEqual('value', self.cache.get('key'))
        self.assertTrue(self.cache.put('key', 'another value'))
        self.assertEqual('another value', self.cache.get('key'))
        self.cache.flush()
        self.assertIsNone(self.cache.get('key'))
