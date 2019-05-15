from unittest import TestCase

from longitude.core.common.query_response import LongitudeQueryResponse

from ..caches.base import LongitudeCache
from longitude.core.tests.utils import async_test


class TestLongitudeCache(TestCase):
    def test_generate_key(self):
        import string
        import random
        # The interesting point here is to ensure that it is extremely difficult to have collisions
        # We will test really similar payloads and test for unique hashes
        queries_population = 100000

        QUERY_PATTERN = "SELECT * FROM table_%s"
        random_queries = set(
            [QUERY_PATTERN % ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=20)
            ) for _ in range(queries_population)]
        )

        keys = set([LongitudeCache.generate_key(q, {}) for q in random_queries])

        # By using sets we ensure uniqueness.
        self.assertEqual(len(random_queries), len(keys))

        # Also, function must return ALWAYS the same value for the same query, regarless of
        # how many times the function is called
        unique_key = set(
            [LongitudeCache.generate_key('SOME_QUERY_OVER_AND_OVER', {}) for _ in range(100)]
        )
        self.assertEqual(1, len(unique_key))

    def test_get_nor_put_are_implemented_in_base_class(self):
        cache = LongitudeCache()
        with self.assertRaises(NotImplementedError):
            cache.get('some_query', {})
        with self.assertRaises(NotImplementedError):
            cache.put('some_query', payload=LongitudeQueryResponse())

    @async_test
    async def test_get_nor_put_async_are_implemented_in_base_class(self):
        cache = LongitudeCache()
        with self.assertRaises(NotImplementedError):
            await cache.get_async('some query', {})
        with self.assertRaises(NotImplementedError):
            await cache.put_async('some query', payload=LongitudeQueryResponse())
