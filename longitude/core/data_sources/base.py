import logging
import os

from ..caches.base import LongitudeCache
from ..common.exceptions import (LongitudeQueryCannotBeExecutedException,  # noqa
                                 LongitudeRetriesExceeded)


class DataSource():

    def __init__(self, options={}):
        """Base class to create an instance of a data source. This class is used as
        base class for specific interfaces.
        :param cache: Object. Must be a LongitudeCache subclass.
        """
        self.log = logging.getLogger(self.__class__.__module__)
        self._cache = options.get('cache')
        self._use_cache = (True and self._cache)

        if self._cache:
            if not isinstance(self._cache, LongitudeCache):
                raise TypeError('Cache must derive from LongitudeCache or be None')

    def enable_cache(self):
        if self._cache:
            self._use_cache = True
        else:
            self.log.warning('DataSource.enable_cache: Cache not available')

    def disable_cache(self):
        self._use_cache = False

    def query(self, query_template, params=None, cache=True, expiration_time_s=None,
              query_config=None, **opts):
        """
        This method has to be called to interact with the data source. Each children class will
        have to implement its own .execute_query(...) with the specific behavior for each interface.

        :param query_template: Unformatted SQL query
        :param params: Values to be passed to the query when formatting it
        :param cache: Boolean to indicate if this specific query should use cache or not
            (default: True)
        :param expiration_time_s: If using cache and cache supports expiration, amount of seconds
            for the payload to be stored
        :param query_config: Specific query configuration. If None, the default one will be used.
        :param opts:
        :return: Result of querying the database
        """
        if params is None:
            params = {}

        response = None
        if self._cache and self._use_cache and cache:
            response = self._cache.get(query_template, params)

        if response:
            response.mark_as_cached()
        else:
            response = self.execute_query(
                query_template=query_template,
                params=params,
                query_config=query_config,
                **opts
            )

            response = self.parse_response(response)
            if self._cache and self._use_cache and cache:
                self._cache.put(
                    query_template,
                    payload=response,
                    query_params=params,
                    expiration_time_s=expiration_time_s
                )

        return response

    def execute_query(self, query_template, params, query_config, **opts):
        """
        :raise LongitudeQueryCannotBeExecutedException
        :param formatted_query:
        :param query_config:
        :param opts:
        :return:
        """
        raise NotImplementedError

    def parse_response(self, response):
        """"
        :param response from an succesfully executed query
        :return: A LongitudeQueryResponse object
        """
        raise NotImplementedError

    def flush_cache(self):
        if self._cache:
            self._cache.flush()

    def copy_from_csv(self, csv_file_absolute_path, to_table=None):
        """
        This method pushes the content of the csv file into the desired table.

        CSV File MUST have header and delimiter must be ',' (comma)

        :param csv_file_absolute_path:
        :param to_table:
        :return:
        """

        with open(csv_file_absolute_path, 'rb') as f:
            if to_table is None:
                to_table = os.path.basename(csv_file_absolute_path)
            return self.copy_from(data=f, filepath=csv_file_absolute_path, to_table=to_table)

    def copy_from(self, data, filepath, to_table):
        raise NotImplementedError

    def read_dataframe(self, table_name='', *args, **kwargs):
        raise NotImplementedError

    def query_dataframe(self, query='', *args, **kwargs):
        raise NotImplementedError

    def write_dataframe(self, df, table_name='', *args, **kwargs):
        raise NotImplementedError
