# from longitude.core.data_sources.dbapi.exceptions import *
from longitude.core.data_sources.carto import CartoDataSource


def connect(user, api_key, options):
    conn = Connection(user, api_key, options)
    return conn


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
    description = None

    rowcount = -1

    def close(self):
        pass

    def execute(self, operation, parameters={}):
        self._result_index = 0
        self._result = self.execute_query(operation, parameters)

    def executemany(self, operation, seq_of_parameters=[]):
        self.execute(operation)

    def fetchone(self):
        row = None
        if self._result and (self._result_index < self._result.get('total_rows')):
            row = self._result.get('rows')[self._result_index]
            self._result_index = self._result_index + 1
        return row

    def fetchmany(self, size=10):
        pass

    def fetchall(self):
        return self._result.get('rows')

    def setinputsizes(self, sizes):
        return None

    def setoutputsize(self, size, column=None):
        pass  # do nothing
