import re
import logging


class LongitudeBaseException(Exception):
    pass


class LongitudeRetriesExceeded(LongitudeBaseException):
    pass


class LongitudeQueryCannotBeExecutedException(LongitudeBaseException):
    pass


class LongitudeWrongQueryException(LongitudeBaseException):
    pass


def is_write_query(sql_statement):
    """
    Check if a query string is a write query
    """
    write_cmds = 'drop|delete|insert|update|grant|execute|perform|create|begin|commit|alter'
    is_write = re.search(write_cmds, sql_statement.lower())
    return is_write


class DataSourceQueryConfig:
    def __init__(self, enable_writing=False, retries=0, custom=None):
        self.enable_writing = enable_writing
        self.retries = retries

        self.custom = custom or {}  # Depending on the specific interface, sometimes we also need to specify per-query values

    def copy(self):
        return DataSourceQueryConfig(self.enable_writing, self.retries, self.custom)


class DataSource:
    default_config = {}

    def __init__(self, config=None):
        self.logger = logging.getLogger(self.__class__.__module__)
        self._default_query_config = DataSourceQueryConfig()

        if config is None:
            config = {}

        if not isinstance(config, dict):
            raise TypeError('Config object must be a dictionary')

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

    def enable_writing_queries(self):
        self._default_query_config.enable_writing = True

    def disable_writing_queries(self):
        self._default_query_config.enable_writing = False

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
        This method must be implemented by children classes.
        :return: True if setup() call was successful. False if not.
        """
        return NotImplementedError

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

    def query(self, statement, params=None, query_config=None, **opts):
        """
        This method has to be called to interact with the data source. Each children class will have to implement
        its own .execute_query(...) with the specific behavior for each interface.

        :param statement: Unformatted SQL query
        :param params: Values to be passed to the query when formatting it
        :param query_config: Specific query configuration. If None, the default one will be used.
        :param opts:
        :return: Result of querying the database
        """
        if params is None:
            params = {}

        if query_config is None:
            query_config = self._default_query_config

        if is_write_query(statement):
            raise LongitudeWrongQueryException('Aborted query. No write queries allowed.')

        for r in range(self.tries):
            try:
                return self.execute_query(formatted_statement=statement.format(**params), query_config=query_config,
                                          **opts)
            except LongitudeQueryCannotBeExecutedException:
                self.logger.error('Query could not be executed. Retries left: %d' % (self.tries - r))

        raise LongitudeRetriesExceeded

    def execute_query(self, formatted_statement, query_config, **opts):
        """

        :raise LongitudeQueryCannotBeExecutedException
        :param formatted_statement:
        :param query_config:
        :param opts:
        :return:
        """
        raise NotImplementedError
