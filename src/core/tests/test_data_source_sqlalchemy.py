from unittest import TestCase, mock
from ..data_sources.postgres.sqlalchemy import SQLAlchemyDataSource

TESTED_MODULE_PATH = 'src.core.data_sources.postgres.sqlalchemy.%s'


class TestSQLAlchemyDataSource(TestCase):

    def test_default_configuration_loads(self):
        with self.assertLogs(level='INFO') as log_test:
            carto_ds = SQLAlchemyDataSource()
            module_name = 'src.core.common.config'
            self.assertEqual(log_test.output,
                             ['INFO:%s:db key is using default value' % module_name,
                              'INFO:%s:host key is using default value' % module_name,
                              'INFO:%s:password key is using default value' % module_name,
                              'INFO:%s:port key is using default value' % module_name,
                              'INFO:%s:user key is using default value' % module_name
                              ]
                             )

            self.assertEqual('', carto_ds.get_config('db'))
            self.assertEqual('localhost', carto_ds.get_config('host'))
            self.assertEqual('', carto_ds.get_config('password'))
            self.assertEqual(5432, carto_ds.get_config('port'))
            self.assertEqual('postgres', carto_ds.get_config('user'))

    @mock.patch(TESTED_MODULE_PATH % 'declarative_base')
    def test_base_class(self, alchemy_base_mock):
        alchemy_base_mock.return_value = object()
        carto_ds = SQLAlchemyDataSource()
        self.assertIsNotNone(carto_ds.base_class)  # Here, first time instance is created
        self.assertIsNotNone(carto_ds.base_class)  # Here, instance is recovered
        alchemy_base_mock.assert_called_once()  # Base class is only created once by our wrapper

    @mock.patch(TESTED_MODULE_PATH % 'SQLAlchemyDataSource.base_class')
    def test_create_all(self, base_class_mock):
        base_class_mock.metadata.create_all = mock.MagicMock()
        carto_ds = SQLAlchemyDataSource()
        carto_ds.create_all()
        base_class_mock.metadata.create_all.assert_called_once()

    def test_setup(self):
        carto_ds = SQLAlchemyDataSource()
        with mock.patch(TESTED_MODULE_PATH % 'create_engine') as fake_create_engine:
            carto_ds.setup()
            fake_create_engine.assert_called_once()
