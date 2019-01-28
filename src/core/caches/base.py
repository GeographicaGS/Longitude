import hashlib
import logging
from ..data_sources.util import is_write_query


class LongitudeCache:
    default_config = {}

    def __init__(self, config=None):
        self._config = config or self.default_config
        self.logger = logging.getLogger(self.__class__.__module__)

    @staticmethod
    def generate_key(formatted_query):
        """
        This is the default key generation algorithm, based in a digest from the sha256 hash of the query.

        Override this method to provide your own key generation in case you need a specific way to store your cache.

        :param formatted_query: Final query as it should be asked to the database
        :return: An (most likely) unique hash, generated from the query text
        """

        return hashlib.sha256(formatted_query.encode('utf-8')).hexdigest()

    def setup(self):
        raise NotImplementedError

    @property
    def is_ready(self):
        raise NotImplementedError

    def get(self, formatted_query):
        if is_write_query(formatted_query):
            return None
        else:
            return self.execute_get(self.generate_key(formatted_query))

    def put(self, formatted_query, payload):
        if is_write_query(formatted_query):
            return None
        else:
            self.execute_put(self.generate_key(formatted_query), payload)

    def execute_get(self, key):
        """
        Custom get action over the cache.

        :return: Query response as it was saved if hit. None if miss.
        """
        raise NotImplementedError

    def execute_put(self, key, payload):
        """
        Custom put action over the cache.

        :return: True if key was overwritten. False if key was new in the cache.
        """
        raise NotImplementedError

    def flush(self):
        """
        Custom action to make the cache empty

        :return:
        """
        raise NotImplementedError
