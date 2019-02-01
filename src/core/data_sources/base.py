import logging
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

    def __init__(self, config=None, cache_class: Type[LongitudeCache] = None):
        super().__init__(config=config)
        self.logger = logging.getLogger(self.__class__.__module__)
        self._default_query_config = DataSourceQueryConfig()
        self._use_cache = True
        self._cache = None

        if cache_class:
            if not issubclass(cache_class, LongitudeCache):
                raise TypeError('Cache must derive from LongitudeCache or be None')
            else:
                self._cache = cache_class(config=config.get('cache'))

    def setup(self):
        if self._cache:
            self._cache.setup()

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

    @property
    def is_ready(self):
        """
        This method must be implemented by children classes to reflect that setup was ok and must call super().is_ready
        :return: True if setup() call was successful. False if not.
        """
        return not self._cache or self._cache.is_ready

    def enable_cache(self):
        self._use_cache = True

    def disable_cache(self):
        self._use_cache = False

    def query(self, query_template, params=None, use_cache=True, needs_commit=False, query_config=None, **opts):
        """
        This method has to be called to interact with the data source. Each children class will have to implement
        its own .execute_query(...) with the specific behavior for each interface.

        :param query_template: Unformatted SQL query
        :param params: Values to be passed to the query when formatting it
        :param use_cache: Boolean to indicate if this specific query should use cache or not (default: True)
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
        if self._cache and self._use_cache and use_cache:
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
                    if self._cache and self._use_cache and use_cache:
                        self._cache.put(query_template, payload=normalized_response, query_params=params)

                    return normalized_response
                except LongitudeQueryCannotBeExecutedException:
                    self.logger.error('Query could not be executed. Retries left: %d' % (self.tries - r))
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
