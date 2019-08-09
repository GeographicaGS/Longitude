# Basic Carto Python DBAPI connector to work with alembic
# specs:   https://www.python.org/dev/peps/pep-0249/

from longitude.core.data_sources.carto import CartoDataSource
from sqlalchemy.dialects import registry

registry.register("carto", "longitude.tools.sqlalchemy.dialect", "CartoDialect")
registry.register("carto.pyodbc", "longitude.tools.sqlalchemy.dialect", "CartoDialect")


def connect(user, api_key, options={}):
    return Connection(user, api_key, options)


def apilevel():
    return '2.0'


def threadsafety():
    return 1


def paramstyle():
    # Prefferible: return 'pyformat'
    # but by now let's keep the current CartoDataSource.execute_query's format:
    return 'format'


class Connection:

    def __init__(self, *args, **kwargs):
        self.conn = Cursor(*args, **kwargs)

    def close(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def cursor(self):
        return self.conn


class Cursor(CartoDataSource):
    # TODO: Get information about tables so that we can properly format query parameters
    #   at execute and executemany methods.

    # Sequence of (name, type_code, display_size, internal_size, precision, scale, null_ok)
    #  - fake descriptor:
    description = [('carto', None, 10, 10, 1, 10, True)]

    rowcount = -1

    def close(self):
        pass

    def execute(self, operation, parameters={}):
        self._result_index = 0
        self._result = self.execute_query(operation, parameters, query_config={})

    def executemany(self, operation, seq_of_parameters=[]):
        self.execute(operation)

    def fetchone(self):
        row = None
        if self._result and (self._result_index < self._result.get('total_rows')):
            row = self._result.get('rows')[self._result_index]
            self._result_index = self._result_index + 1
        return list(row.values())

    def fetchmany(self, size=10):
        # TODO
        pass

    def fetchall(self):
        return self._result.get('rows')

    def setinputsizes(self, sizes):
        return None

    def setoutputsize(self, size, column=None):
        pass  # do nothing
