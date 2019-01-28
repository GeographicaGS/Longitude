from unittest import TestCase, mock
from ..caches.base import LongitudeCache


class TestLongitudeCache(TestCase):
    def test_generate_key(self):
        import string
        import random
        # The interesting point here is to ensure that it is extremely difficult to have collisions
        # We will test really similar payloads and test for unique hashes
        queries_population = 100000

        QUERY_PATTERN = "SELECT * FROM table_%s"
        random_queries = set([QUERY_PATTERN % ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
                              for _ in range(queries_population)])

        keys = set([LongitudeCache.generate_key(q) for q in random_queries])

        # By using sets we ensure uniqueness.
        self.assertEqual(len(random_queries), len(keys))

        # Also, function must return ALWAYS the same value for the same query, regarless of how many times the
        #  function is called
        unique_key = set([LongitudeCache.generate_key('SOME_QUERY_OVER_AND_OVER') for _ in range(100)])
        self.assertEqual(1, len(unique_key))

    @mock.patch('src.core.caches.base.is_write_query')
    def test_get_and_put_returns_none_for_write_queries(self, is_write_mock):
        is_write_mock.return_value = True
        cache = LongitudeCache()
        self.assertIsNone(cache.get('some_query'))
        self.assertIsNone(cache.put('some_query', payload='whatever'))
        self.assertEqual(2, is_write_mock.call_count)

    @mock.patch('src.core.caches.base.is_write_query')
    def test_get_nor_put_are_implemented_in_base_class(self, is_write_mock):
        is_write_mock.return_value = False
        cache = LongitudeCache()
        with self.assertRaises(NotImplementedError):
            cache.get('some_query')
        with self.assertRaises(NotImplementedError):
            cache.put('some_query', payload='whatever')
        self.assertEqual(2, is_write_mock.call_count)
