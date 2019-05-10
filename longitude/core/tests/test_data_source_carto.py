from unittest import TestCase, mock

from carto.exceptions import CartoException

from ..data_sources.base import LongitudeQueryCannotBeExecutedException
from ..data_sources.carto import CartoDataSource


class TestCartoDataSource(TestCase):

    def test_succesful_query(self):
        ds = CartoDataSource(user='', api_key='')
        ds._sql_client = mock.MagicMock()
        ds._sql_client.send.return_value = {'rows': [], 'time': 42.0, 'fields': {}, 'total_rows': 0}
        result = ds.query('some query')
        ds._sql_client.send.assert_called_with(
            'some query',
            do_post=False,
            format='json',
            parse_json=True
        )
        self.assertEqual([], result.rows)
        self.assertEqual(42, result.meta['response_time'])

    def test_wrong_query(self):
        ds = CartoDataSource(user='', api_key='')
        ds._sql_client = mock.MagicMock()
        ds._sql_client.send.side_effect = CartoException
        with self.assertRaises(LongitudeQueryCannotBeExecutedException):
            ds.query('some irrelevant query')
