import logging
import os
from time import time
from typing import Type

from ..caches.base import LongitudeCache
from ..common.config import LongitudeConfigurable
from ..common.exceptions import (LongitudeQueryCannotBeExecutedException,
                                 LongitudeRetriesExceeded)


class DataSourceQueryConfig:
    def __init__(self, retries=0, custom=None):
        self.retries = retries

        # Depending on the specific interface (i.e.: CARTO, Postgres...), we might also need to specify per-query values
        self.custom = custom or {}

    def copy(self):
        return DataSourceQueryConfig(self.retries, self.custom)


class DataSource(LongitudeConfigurable):
    # Every  data source is registered at class level so other domain entities can access them (APIs, views...)
    data_sources = {}

    def __init__(self, config='', cache_class: Type[LongitudeCache] = None, cache=None):
        """
        Base class to create an instance of a data source. This class is used as base class for specific interfaces.

        :param config: Label as it appears in the configuration (or environment variable as LONGITUDE__{name}__...} or
        a dictionary with a valid configuration.
        :param cache_class: If provided, this class will be instantiated with the configuration from the datasource
         cache. Cannot be provided at the same time as cache.
        :param cache: If provided, this cache instance will be used as cache for the datasource. Cache configuration in
         the datasource config will be ignored. Cannot be provided at the same time ascache_class.
        """
        super().__init__(config=config)
        self.logger = logging.getLogger(self.__class__.__module__)
        self._default_query_config = DataSourceQueryConfig()
        self._use_cache = True
        self._cache = None

        if cache_class and cache:
            raise RuntimeError('Either cache_class or cache can be provided, but not both at the same time.')

        if cache_class:
            if not issubclass(cache_class, LongitudeCache):
                raise TypeError('Cache class must derive from LongitudeCache or be None')
            else:
                self._cache = cache_class('%s.cache' % self.name)

        if cache:
            if not isinstance(cache, LongitudeCache):
                raise TypeError('Cache must be an instance from LongitudeCache or be None')
            else:
                self._cache = cache

        self.data_sources[self.name] = self

    @property
    def is_ready(self):
        """
        This method must be implemented by children classes to reflect that setup was ok and must call super().is_ready
        :return: True if setup() call was successful. False if not.
        """
        return not self._cache or self._cache.is_ready

    @property
    def tries(self):
        return self._default_query_config.retries + 1

    def set_retries(self, value=0):
        """
        Sets the amount of times that a query will be re-asked in case of failure.
        Zero means that there will be no RE-tries, BUT the first try will be done so the query is sent once at least.

        :param value: Amount of desired retries. Negative values will be forced to 0.
        """
        self._default_query_config.retries = max(0, value)

    def set_custom_query_default(self, key, value):
        self._default_query_config.custom[key] = value

    def copy_default_query_config(self):
        """
        Helper for custom queries. When doing a query with some different configuration, copy the default one, modify it
        and pass it to the query.

        :return: A new object with the same content as the current default query config
        """
        return self._default_query_config.copy()

    def enable_cache(self):
        self._use_cache = True

    def disable_cache(self):
        self._use_cache = False

    def committed_query(self, query_template, params=None):
        """
        This is a shortcut for INSERT queries and similar ones dealing with simple update operations.

        Makes a default non-cached query committing the result. If you need to specify more details such as cache or
        query specific values, use .query(...)

        :param query_template: Unformatted SQL query
        :param params: Values to be passed to the query when formatting it
        :return:
        """
        return self.query(query_template, params=params, cache=False, needs_commit=True)

    def cached_query(self, query_template, params=None, expiration_time_s=None):
        """
        This is a shortcut for SELECT queries and similar ones requesting simple data.

        Makes a default cached query. This means that no commit is done and no specific config for the query is
        available. If you need any of these, use .query(...)

        :param query_template: Unformatted SQL query
        :param params: Values to be passed to the query when formatting it
        :param expiration_time_s: Amount of seconds for the payload to be stored (if cache supports this)
        :return: Result of the query
        """
        return self.query(query_template, params=params, expiration_time_s=expiration_time_s)

    def query(self, query_template, params=None, cache=True, expiration_time_s=None, needs_commit=False,
              query_config=None, **opts):
        """
        This method has to be called to interact with the data source. Each children class will have to implement
        its own .execute_query(...) with the specific behavior for each interface.

        :param query_template: Unformatted SQL query
        :param params: Values to be passed to the query when formatting it
        :param cache: Boolean to indicate if this specific query should use cache or not (default: True)
        :param expiration_time_s: If using cache and cache supports expiration, amount of seconds for the payload to be stored
        :param needs_commit: Boolean to indicate if this specific query needs to commit to db (default: False)
        :param query_config: Specific query configuration. If None, the default one will be used.
        :param opts:
        :return: Result of querying the database
        """
        if params is None:
            params = {}

        if query_config is None:
            query_config = self._default_query_config

        normalized_response = None
        if self._cache and self._use_cache and cache:
            start = time()
            normalized_response = self._cache.get(query_template, params)
            if normalized_response:
                normalized_response.profiling['cache_time'] = time() - start

        if normalized_response:
            normalized_response.mark_as_cached()
            return normalized_response
        else:
            for r in range(self.tries):
                try:
                    response = self.execute_query(query_template=query_template,
                                                  params=params,
                                                  needs_commit=needs_commit,
                                                  query_config=query_config,
                                                  **opts)

                    normalized_response = self.parse_response(response)
                    if self._cache and self._use_cache and cache:
                        self._cache.put(
                            query_template,
                            payload=normalized_response,
                            query_params=params,
                            expiration_time_s=expiration_time_s
                        )

                    return normalized_response
                except LongitudeQueryCannotBeExecutedException as e:
                    self.logger.error('Query could not be executed:%s. Retries left: %d' % (e, self.tries - r))
            raise LongitudeRetriesExceeded

    def execute_query(self, query_template, params, needs_commit, query_config, **opts):
        """

        :raise LongitudeQueryCannotBeExecutedException
        :param formatted_query:
        :param needs_commit:
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
        if self._cache and self._cache.is_ready:
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
