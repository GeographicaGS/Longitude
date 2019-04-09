from unittest import TestCase, mock

from ..data_sources.postgres.sqlalchemy import SQLAlchemyDataSource

TESTED_MODULE_PATH = 'longitude.core.data_sources.postgres.sqlalchemy.%s'


class TestSQLAlchemyDataSource(TestCase):

    def setUp(self):
        # We mock the calls to the internal engine creation for all tests
        # As we have a is_ready method, we just ensure that these calls return something
        patcher = mock.patch(TESTED_MODULE_PATH % 'create_engine')
        self.addCleanup(patcher.stop)
        self.create_engine_mock = patcher.start()

        self.create_engine_mock.return_value._connect.return_value = object()

    @mock.patch(TESTED_MODULE_PATH % 'declarative_base')
    def test_base_class(self, alchemy_base_mock):
        alchemy_base_mock.return_value = object()
        carto_ds = SQLAlchemyDataSource()
        self.assertIsNotNone(carto_ds.base_class)  # Here, first time instance is created
        self.assertIsNotNone(carto_ds.base_class)  # Here, instance is recovered
        alchemy_base_mock.assert_called_once()  # Base class is only created once by our wrapper
        self.assertTrue(carto_ds.is_ready)

    @mock.patch(TESTED_MODULE_PATH % 'SQLAlchemyDataSource.base_class')
    def test_create_all(self, base_class_mock):
        base_class_mock.metadata.create_all = mock.MagicMock()
        carto_ds = SQLAlchemyDataSource()
        carto_ds.create_all()
        base_class_mock.metadata.create_all.assert_called_once()
