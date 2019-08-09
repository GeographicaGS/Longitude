# Basic Carto dialect for sqlalchemy:
# ref: https://github.com/zzzeek/sqlalchemy/blob/master/README.dialects.rst

from sqlalchemy.engine import default
from . import pyodbc


class CartoDialect(default.DefaultDialect):

    def __init__(self, *args, **kwargs):
        super(CartoDialect, self).__init__(*args, **kwargs)
        self.dbapi = kwargs.get('dbapi')
        self.paramstyle = pyodbc.paramstyle()

    def do_rollback(self, connection):
        pass

    def do_execute(self, cursor, statement, parameters, context):
        self.cursor = cursor
        return cursor.execute(statement, parameters)

    def connect(self, *args, **kwargs):
        return self.dbapi.connect(*args, **kwargs)

    @classmethod
    def dbapi(cls):
        return pyodbc

    def has_table(self, connection, table_name, schema=None):
        sql = ''
        if schema is None:
            sql = f'''
                select relname
                from pg_class c join pg_namespace n
                    on n.oid=c.relnamespace
                where pg_catalog.pg_table_is_visible(c.oid)
                    and relname='{table_name}'
            '''
        else:
            sql = f'''
                select relname
                from pg_class c join pg_namespace n
                on n.oid=c.relnamespace where n.nspname='{schema}'
                    and relname='{table_name}'
            '''
        cursor = connection.execute(sql)
        return bool(cursor.fetchone())

    def get_table_names(self, connection, schema=None, **kw):
        result = connection.execute(f'''
            SELECT c.relname FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = '{schema or self.default_schema_name}'
            AND c.relkind in ('r', 'p')
        ''')
        return [name for name, in result]
