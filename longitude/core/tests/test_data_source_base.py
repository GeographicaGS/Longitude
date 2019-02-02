import os
from unittest import TestCase, mock

from ..caches.base import LongitudeCache
from ..common.query_response import LongitudeQueryResponse
from ..data_sources.base import DataSource, DataSourceQueryConfig


def load_raw_text(filename):
    file_path = os.path.join(os.path.dirname(__file__), 'raw_text', filename)
    with open(file_path, 'r') as f:
        return f.read()


class TestDataSourceQueryConfig(TestCase):
    def test_copy(self):
        a = DataSourceQueryConfig()
        b = a.copy()

        self.assertNotEqual(a, b)
        self.assertEqual(a.__dict__, b.__dict__)


class TestDataSource(TestCase):
    def setUp(self):
        import pickle

        class FakeCache(LongitudeCache):

            @staticmethod
            def generate_key(query_template, query_parameters):
                if query_template == 'some_query_in_cache':
                    return 'hit'
                return 'miss'

            def setup(self):
                pass

            @property
            def is_ready(self):
                return True

            def execute_get(self, key):
                if key == 'hit':
                    return pickle.dumps(LongitudeQueryResponse())
                return None

            def execute_put(self, key, payload, expiration_time_s=None):
                return True

        self._cache_class = FakeCache

    def test_cache_must_extend_longitude_cache(self):
        class PoorlyImplementedCache:
            pass

        with self.assertRaises(TypeError):
            DataSource({}, cache_class=PoorlyImplementedCache)

    def test_cache_hit(self):
        ds = DataSource({}, cache_class=self._cache_class)
        ds.setup()
        # At high level, ds.query will return a normalized LongitudeQueryResponse
        # In this test we are interested in triggering that call to the parse function that would return such object,
        # but we do not care, in the abstract class, about what content is generated there.
        self.assertTrue(ds.query('some_query_in_cache').comes_from_cache)

    @mock.patch('longitude.core.data_sources.base.DataSource.parse_response')
    @mock.patch('longitude.core.data_sources.base.DataSource.execute_query')
    def test_cache_miss(self, execute_query_mock, parse_response_mock):
        ds = DataSource({}, cache_class=self._cache_class)
        ds.setup()
        execute_query_mock.return_value = 'some response from the server'
        parse_response_mock.return_value = LongitudeQueryResponse(profiling={'value': 42})
        self.assertEqual(42, ds.query('some_query_not_in_cache').profiling['value'])
        parse_response_mock.assert_called_once_with('some response from the server')

    def test_abstract_methods_are_not_implemented(self):
        ds = DataSource({})

        with self.assertRaises(NotImplementedError):
            ds.query(query_template='whatever')

    def test_is_ready(self):
        class FakeReadyCache(LongitudeCache):
            def setup(self):
                pass

            @property
            def is_ready(self):
                return True

        class FakeNotReadyCache(LongitudeCache):
            def setup(self):
                pass

            @property
            def is_ready(self):
                return False

        ds = DataSource(config={}, cache_class=FakeReadyCache)
        self.assertTrue(ds.is_ready)
        ds = DataSource(config={}, cache_class=FakeNotReadyCache)
        self.assertFalse(ds.is_ready)

    def test_copy_default_query_config(self):
        ds = DataSource({})
        the_copy = ds.copy_default_query_config()
        self.assertNotEqual(the_copy, ds._default_query_config)
        self.assertEqual(the_copy.__dict__, ds._default_query_config.__dict__)
