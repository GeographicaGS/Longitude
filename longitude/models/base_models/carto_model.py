"""
Base module for CARTO
"""

import re
import hashlib
import pickle
import redis
import os
import time
import json
import urllib.parse

from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient, BatchSQLClient
from carto.exceptions import CartoException
from longitude.config import cfg
from .database_base_model import DatabaseBaseModel

CartoModelException = CartoException


class CartoModel(DatabaseBaseModel):
    """
    CARTO Model base class
    """

    def __init__(self, config=None):
        """
        Constructor
        """
        self.conf = dict(cfg)
        self.conf.update(config)
        self._carto_api_key = self.conf['CARTO_API_KEY']
        self._carto_user = self.conf['CARTO_USER']
        self._cartouser_url = 'https://{0}.carto.com'.format(self._carto_user)

        if 'CARTO_ONPREMISES_URL' in self.conf and self.conf['CARTO_ONPREMISES_URL'] != None:
            self._cartouser_url = self.conf['CARTO_ONPREMISES_URL']

        super().__init__()

    def query(self, sql_query, opts=None, arguments=None, **kwargs):
        """
        Run a query against CARTO
        """

        try:
            if not opts:
                opts = {}

            opts.update(kwargs)

            cache = self.conf['CACHE'] and opts.get('cache', True)
            write_qry = opts.get('write_qry', False)
            batch = opts.get('batch', False)

            if not write_qry and self._is_write_query(sql_query):
                raise CartoModelException('Aborted query. No write queries allowed.')

            if write_qry or batch:
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

            # The query does not exist in redis, so do query in carto and save result in redis.

            result = self._do_carto_query(sql_query, opts)

            expire = opts.get('cache_expire', self.conf['CACHE_EXPIRE'])
            cache_group = opts.get('cache_group', None)

            p = self._redis.pipeline()

            p.set(sql_query_hash, pickle.dumps(result), expire)

            if cache_group is not None:
                p.sadd(cache_group, sql_query_hash)
                p.expire(cache_group, expire)

            p.execute()

            return result

        except CartoException as err:
            raise CartoModelException(err)

    def _do_carto_query(self, sql_query, opts):

        parse_json = opts.get('parse_json', True)
        do_post = opts.get('do_post', True)
        format_query = opts.get('format', None)
        batch = opts.get('batch', False)
        retries = opts.get('retries', 5)

        auth_client = APIKeyAuthClient(api_key=self._carto_api_key, base_url=self._cartouser_url)

        if batch:
            # Run using batch API
            batch_sql = BatchSQLClient(auth_client)
            job = None

            for retry_number in range(retries):
                try:
                    job = batch_sql.create(sql_query)

                    if job:
                        break

                except Exception as carto_exception:
                    if retry_number == retries - 1:
                        raise carto_exception
                    else:
                        time.sleep(3)
                        continue

            carto_sql_api = urllib.parse.urljoin(self._cartouser_url+'/', 'api/v2/sql')

            print('Job status: {0}/job/{1}?api_key={2}'.format(carto_sql_api, job['job_id'], self._carto_api_key))

            finished = self._finished_batch_query(auth_client, job['job_id'])
            while not finished:
                time.sleep(1)
                finished = self._finished_batch_query(auth_client, job['job_id'])
            return finished

        else:
            # Run using SQL API
            sql = SQLClient(auth_client, api_version='v2')
            res = None

            for retry_number in range(retries):
                try:
                    res = sql.send(sql_query, parse_json, do_post, format_query)

                    if res:
                        break

                except CartoException as carto_exception:
                    if retry_number == retries - 1:
                        raise carto_exception
                    else:
                        time.sleep(5)
                        continue

        if format_query is None:
            return res['rows']

        return res

    def _finished_batch_query(self, auth_client, job_id):
        """
        Private method for checking batch query status
        """
        try:
            batch_sql = BatchSQLClient(auth_client)
            job = batch_sql.read(job_id)
            if not job or job['status'] == 'failed' or\
                    job['status'] == 'canceled' or job['status'] == 'unknown':
                raise Exception(
                    'Batch query failed: {0}'.format(json.dumps(job)))

            elif job['status'] == 'done':
                return True

            else:
                return False

        except CartoException as exc:
            print('Error executing polling of a batch query in Carto: {0}'.format(exc))
            return False
