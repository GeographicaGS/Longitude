import logging
from typing import Type

from ..caches.base import LongitudeCache


class LongitudeBaseException(Exception):
    pass


class LongitudeRetriesExceeded(LongitudeBaseException):
    pass


class LongitudeQueryCannotBeExecutedException(LongitudeBaseException):
    pass


class LongitudeWrongQueryException(LongitudeBaseException):
    pass


class DataSourceQueryConfig:
    def __init__(self, retries=0, custom=None):
        self.retries = retries

        # Depending on the specific interface (i.e.: CARTO, Postgres...), we might also need to specify per-query values
        self.custom = custom or {}

    def copy(self):
        return DataSourceQueryConfig(self.retries, self.custom)


class DataSource:
    default_config = {}

    def __init__(self, config=None, cache_class: Type[LongitudeCache] = None):
        self.logger = logging.getLogger(self.__class__.__module__)
        self._default_query_config = DataSourceQueryConfig()
        self._use_cache = True
        self._cache = None

        if config is None:
            config = {}

        if not isinstance(config, dict):
            raise TypeError('Config object must be a dictionary')

        if cache_class:
            if not issubclass(cache_class, LongitudeCache):
                raise TypeError('Cache must derive from LongitudeCache or be None')
            else:
                self._cache = cache_class(config=config.get('cache'))

        default_keys = set(self.default_config.keys())
        config_keys = set(config.keys())
        unexpected_config_keys = list(config_keys.difference(default_keys))
        using_defaults_for = list(default_keys.difference(config_keys))

        unexpected_config_keys.sort()
        using_defaults_for.sort()

        for k in unexpected_config_keys:
            self.logger.warning("%s is an unexpected config value" % k)

        for k in using_defaults_for:
            self.logger.info("%s key is using default value" % k)

        self._config = config

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

    def get_config(self, key: str):
        """
        Getter for configuration values
        :param key: Key in the configuration dictionary
        :return: Current value of the chosen key
        """
        try:
            return self._config[key]
        except KeyError:
            try:
                return self.default_config[key]
            except KeyError:
                return None

    def enable_cache(self):
        self._use_cache = True

    def disable_cache(self):
        self._use_cache = False

    def query(self, statement, params=None, use_cache=True, query_config=None, **opts):
        """
        This method has to be called to interact with the data source. Each children class will have to implement
        its own .execute_query(...) with the specific behavior for each interface.

        :param statement: Unformatted SQL query
        :param params: Values to be passed to the query when formatting it
        :param use_cache: Bool to indicate if this specific query should use cache or not (default: True)
        :param query_config: Specific query configuration. If None, the default one will be used.
        :param opts:
        :return: Result of querying the database
        """
        if params is None:
            params = {}

        if query_config is None:
            query_config = self._default_query_config

        formatted_query = statement.format(**params)

        normalized_response = None
        if self._cache and self._use_cache and use_cache:
            normalized_response = self._cache.get(formatted_query)

        if normalized_response:
            normalized_response.mark_as_cached()
            return normalized_response
        else:
            for r in range(self.tries):
                try:
                    response = self.execute_query(formatted_query=formatted_query,
                                                  query_config=query_config,
                                                  **opts)
                    normalized_response = self.parse_response(response)
                    if self._cache and self._use_cache and use_cache:
                        self._cache.put(formatted_query, normalized_response)

                    return normalized_response
                except LongitudeQueryCannotBeExecutedException:
                    self.logger.error('Query could not be executed. Retries left: %d' % (self.tries - r))
                raise LongitudeRetriesExceeded

    def execute_query(self, formatted_query, query_config, **opts):
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
        if self._cache and self._cache.is_ready:
            self._cache.flush()


class LongitudeQueryResponse:
    def __init__(self, rows=None, fields=None, profiling=None):
        self.rows = rows or []
        self.fields = fields or {}
        self.profiling = profiling or {}
        self._from_cache = False

    @property
    def comes_from_cache(self):
        return self._from_cache

    def mark_as_cached(self):
        self._from_cache = True

    def preview_top(self):
        return self._preview(10)

    def preview_bottom(self):
        return self._preview(-10)

    def _preview(self, limit):
        def render_line(values):
            def render_value(value):
                value = str(value)
                if len(value) > 20:
                    value = value[:14] + ' (...)'
                return value

            values = [render_value(v) + '\t' for v in values]
            return '| ' + '| '.join(values) + '\t|'

        if limit > 0:
            preview_list = self.rows[:limit]
        else:
            preview_list = self.rows[limit:]

        lines = [render_line(l) for l in preview_list]
        headers = [k for k, v in self.fields.items()]

        lines = [render_line(headers)] + lines
        render = '\n'.join(lines)
        if self.profiling and 'response_time' in self.profiling.keys():
            render += '\n\n' + '... time = %f' % self.profiling['response_time']
        return render

    def __str__(self):
        return self.preview_top()
