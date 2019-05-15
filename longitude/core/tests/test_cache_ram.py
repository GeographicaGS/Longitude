from unittest import TestCase

from longitude.core.common.query_response import LongitudeQueryResponse

from ..caches.ram import RamCache
from longitude.core.tests.utils import async_test


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
        self.assertFalse(self.cache.put('key', payload, expiration_time_s=1))
        self.assertEqual(42, self.cache.get('key').meta['value'])

        self.cache.flush()
        self.assertIsNone(self.cache.get('key'))

    @async_test
    async def test_read_write_flush_cycle_async(self):
        self.assertIsNone(await self.cache.get_async('fake_key'))
        payload = LongitudeQueryResponse()
        payload.meta['value'] = 42
        self.assertTrue(await self.cache.put_async('key', payload))

        result = await self.cache.get_async('key')
        self.assertEqual(42, result.meta['value'])

        await self.cache.flush_async()
        self.assertIsNone(await self.cache.get_async('key'))
