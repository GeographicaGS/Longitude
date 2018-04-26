import redis
import re

from abc import ABC, abstractmethod
from ...config import cfg


class DatabaseBaseModel(ABC):

    def __init__(self):
        if cfg['CACHE']:
            self._redis = redis.StrictRedis(host=cfg['REDIS_HOST'], port=cfg['REDIS_PORT'], db=cfg['REDIS_DB'])
        else:
            self._redis = None

    @staticmethod
    def _is_write_query(sql_query):
        """
        Check if query is a write query
        """
        write_cmds = 'drop|delete|insert|update|grant|execute|perform|create|begin|commit|alter'
        is_write = re.search(write_cmds, sql_query.lower())
        if is_write:
            return True

    @abstractmethod
    def query(self, sql_query, opts=None, arguments=None, **kwargs):
        pass

    def cache_clear(self, cache_group=None):
        """
        Clear the query cache. If a string is given as first argument,
        remove only keys whose group name matches the provided string.
        """

        if cache_group is None:
            self._redis.flushall()
        else:
            group_keys = self._redis.smembers(cache_group)

            if group_keys:
                p = self._redis.pipeline()

                p.srem(cache_group, *group_keys)
                p.delete(*group_keys)

                p.execute()