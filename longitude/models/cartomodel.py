"""
Base module for CARTO
"""

import re
import hashlib
import pickle
import redis
import os

from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
from carto.exceptions import CartoException
from ..config import cfg

CartoModelException = CartoException

class CartoModel:
    """
    CARTO Model base class
    """

    def __init__(self, config=None):
        """
        Constructor
        """
        self._carto_api_key = cfg['CARTO_API_KEY']
        self._carto_user = cfg['CARTO_USER']
        if cfg['CACHE']:
            self._redis = redis.StrictRedis(host=cfg['REDIS_HOST'], port=cfg['REDIS_PORT'], db=cfg['REDIS_DB'])
        else:
            self._redis = None

    @staticmethod
    def _get_auth_client(api_key, carto_user):
        """
        Create the client
        """
        cartouser_url = 'https://{0}.carto.com'.format(carto_user)
        return APIKeyAuthClient(cartouser_url, api_key)

    @staticmethod
    def _is_write_query(sql_query):
        """
        Check if query is a write query
        """
        write_cmds = 'drop|delete|insert|update|grant|execute|perform|create|begin|commit|alter'
        is_write = re.search(write_cmds, sql_query.lower())
        if is_write:
            return True

    def query(self, sql_query, opts=None):
        """
        Run a query against CARTO
        """

        try:
            if not opts:
                opts = {}

            cache = cfg['CACHE'] and opts.get('cache', True)
            write_qry = opts.get('write_qry', False)

            if not write_qry and self._is_write_query(sql_query):
                raise CartoModelException('Aborted query. No write queries allowed.')

            if write_qry:
                cache = False

            if not cache:
                result = self._do_carto_query(sql_query, opts)
                return result

            # sql_query hash
            sql_query_hash = hashlib.sha256(sql_query.encode('utf-8')).hexdigest()

            # get results from redis: key=sql_query_hash
            result = self._redis.get(sql_query_hash)

            # The query exists in redis, so de-serialize and return its value
            if result is not None:
                return pickle.loads(result)

            # The query not exists in redis, so do query in carto and save result in redis.

            result = self._do_carto_query(sql_query, opts)

            expire = opts.get('cache_expire', cfg['CACHE_EXPIRE'])

            self._redis.set(sql_query_hash, pickle.dumps(result), expire)

            return result

        except CartoException as err:
            raise CartoModelException(err)

    def _do_carto_query(self, sql_query, opts):

        parse_json = opts.get('parse_json', True)
        do_post = opts.get('do_post', True)
        format_query = opts.get('format', None)

        auth_client = self._get_auth_client(self._carto_api_key, self._carto_user)
        sql = SQLClient(auth_client, api_version='v2')

        res = sql.send(sql_query, parse_json, do_post, format_query)

        if format_query is None:
            return res['rows']

        return res
