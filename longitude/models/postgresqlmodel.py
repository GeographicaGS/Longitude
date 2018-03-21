import asyncpg
import itertools
from copy import copy
from longitude import config
from collections import OrderedDict


class PostgresqlModel:

    def __init__(self, conn):
        self.conn = conn

    @classmethod
    async def create(cls):
        conn = await asyncpg.connect(
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            host=config.DB_HOST,
            port=config.DB_PORT,
        )

        return cls(conn)

    async def fetch(self, *args, **kwargs):
        res = await self.conn.fetch(*args, **kwargs)

        return [
            OrderedDict(x.items())
            for x
            in (res)
        ]


class CRUDModel:

    table_name = None

    def __init__(self, db_model):
        self.db_model = db_model

    async def list(self, **params):
        sql, params = self.placeholder_to_ordinal(*self.select_sql(params))

        ret = await self._fetch(sql, *params)
        return ret

    async def get(self, oid, **params):
        sql, params = self.placeholder_to_ordinal(*self.select_sql(params, oid))

        ret = await self._fetch(sql, *params)
        return ret

    async def _fetch(self, *args, **kwargs):
        return await self.db_model.fetch(*args, **kwargs)

    def select_sql(self, params, oid=None, columns=tuple('*')):

        where_clause, params = self.where_sql(params, oid)

        return (
            '''
                SELECT 
                    {columns}
                FROM {schema}{table}
                WHERE {where_clause}
            '''.format(
                schema=self.schema,
                table=self.table_name,
                where_clause=where_clause,
                columns=','.join(columns)
            ),
            params
        )

    def where_sql(self, params, oid=None):

        if oid:
            name = self.add_param_name('id', oid, params)

            snippet = '{schema}{table}=${name}'.format(
                schema=self.schema,
                table=self.table_name,
                name=name
            )
        else:
            snippet = 'TRUE'

        return snippet, params

    @property
    def schema(self):
        return config.DB_SCHEMA + '.' if config.DB_SCHEMA \
            else ''

    @staticmethod
    def add_param_name(name, value, params):

        if name in params:
            for i in itertools.count(1):
                name = name + str(i)
                if name not in params:
                    break

        params[name] = value

        return name

    @staticmethod
    def placeholder_to_ordinal(sql, params):
        ordinal_params = []
        for ordinal, named_param in zip(itertools.count(1), params.keys()):
            sql = sql.replace('$' + named_param, '$' + str(ordinal))
            ordinal_params.append(params[named_param])

        return sql, ordinal_params
