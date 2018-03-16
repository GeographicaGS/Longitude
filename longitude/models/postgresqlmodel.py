import asyncpg
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
