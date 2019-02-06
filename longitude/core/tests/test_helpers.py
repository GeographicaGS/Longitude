from unittest import TestCase, mock

from longitude.core.common.helpers import DisabledCache
from longitude.core.data_sources.base import DataSource


class TestHelpers(TestCase):

    @mock.patch('longitude.core.data_sources.base.DataSource', spec=DataSource)
    def test_disable_cache_context_manager_triggers_cache(self, fake_data_source):
        fake_data_source.enable_cache.return_value = None
        fake_data_source.disable_cache.return_value = None
        with DisabledCache(fake_data_source):
            fake_data_source.disable_cache.assert_called_once()
        fake_data_source.enable_cache.assert_called_once()

    @mock.patch('longitude.core.data_sources.base.DataSource')
    def test_disable_cache_context_manager_must_receive_a_data_source(self, fake_data_source):
        with self.assertRaises(TypeError):
            with DisabledCache(fake_data_source):
                print('This text should never be printed')
