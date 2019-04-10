from unittest import TestCase, mock

from longitude.core.common.query_response import LongitudeQueryResponse

from ..caches.ram import RamCache


class TestRedisCache(TestCase):
    cache = None

    def setUp(self):
        self.cache = RamCache()

    def test_serialization_does_nothing(self):
        self.assertEqual('value', self.cache.serialize_payload('value'))
        self.assertEqual('value', self.cache.deserialize_payload('value'))

    def test_read_write_flush_cycle(self):
        self.assertIsNone(self.cache.get('fake_key'))
        payload = LongitudeQueryResponse()
        payload.meta['value'] = 42
        self.assertFalse(self.cache.put('key', payload))
        self.assertEqual(42, self.cache.get('key').meta['value'])

        self.cache.flush()
        self.assertIsNone(self.cache.get('key'))
