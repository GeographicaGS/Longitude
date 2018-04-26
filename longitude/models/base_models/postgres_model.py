import psycopg2
import hashlib
import pickle

from psycopg2.extras import RealDictCursor
from .database_base_model import DatabaseBaseModel
from ...config import cfg


class PostgresModel(DatabaseBaseModel):

    def __init__(self, config=None):
        self._connection = psycopg2.connect(host=cfg['POSTGRES_HOST'], port=cfg['POSTGRES_PORT'],
                                            dbname=cfg['POSTGRES_DB'], user=cfg['POSTGRES_USER'],
                                            password=cfg['POSTGRES_PASSWORD'])
        super().__init__()

    def query(self, sql_query, opts=None, arguments=None, **kwargs):
        try:
            if not opts:
                opts = {}

            opts.update(kwargs)

            cache = cfg['CACHE'] and opts.get('cache', True)
            write_qry = opts.get('write_qry', False)

            if not write_qry and self._is_write_query(sql_query):
                raise Exception('Aborted query. No write queries allowed.')

            if write_qry:
                cache = False

            if not cache:
                result = self._do_postgres_query(sql_query, arguments, opts)
                return result

            # sql_query hash
            sql_query_hash = hashlib.sha256(sql_query.lower().encode('utf-8')).hexdigest()

            # get results from redis: key=sql_query_hash
            result = self._redis.get(sql_query_hash)

            # The query exists in redis, so de-serialize and return its value
            if result is not None:
                return pickle.loads(result)

            # The query not exists in redis, so do query in carto and save result in redis.

            result = self._do_postgres_query(sql_query, arguments, opts)

            expire = opts.get('cache_expire', cfg['CACHE_EXPIRE'])
            cache_group = opts.get('cache_group', None)

            p = self._redis.pipeline()

            p.set(sql_query_hash, pickle.dumps(result), expire)

            if cache_group is not None:
                p.sadd(cache_group, sql_query_hash)
                p.expire(cache_group, expire)

            p.execute()

            return result

        except Exception as err:    # Fix
            raise Exception(err)

    def _do_postgres_query(self, sql_query, arguments, opts):
        cursor = self._connection.cursor(cursor_factory=RealDictCursor)

        binded_query = cursor.mogrify(sql_query, arguments)

        cursor.execute(binded_query)

        if opts.get('write_qry'):
            self._connection.commit()
            return          # fix
        else:
            res = cursor.fetchall()

        return res
