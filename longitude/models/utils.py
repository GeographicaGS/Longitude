"""
Utils module for data models
"""

import re
import json

from collections import namedtuple
from itertools import repeat
from datetime import datetime, date
from psycopg2.extensions import adapt

def get_time_step(dt_step, def_step='1 days'):
    """
    Get PostgreSQL time step
    """
    step = None
    if dt_step == '1h':
        step = '1 hours'
    elif dt_step == '2h':
        step = '2 hours'
    elif dt_step == '4h':
        step = '4 hours'
    elif dt_step == '12h':
        step = '12 hours'
    elif dt_step == '1d':
        step = '1 days'
    elif dt_step == '2d':
        step = '2 days'
    elif dt_step == '3d':
        step = '3 days'
    elif dt_step == '7d':
        step = '7 days'
    else:
        step = def_step

    return step


def stringify_list(src):
    """
    Convert a list to a escaped comma separated string.
    """

    return SQLTrustedString(SQL(','.join(repeat('{}', len(src)))).format(*src))


class SQL(str):
    """
    str wrapper to format SQL parameters safely.
    """

    @staticmethod
    def _must_escape(val):
        return (not isinstance(val, SQLTrustedString)) and isinstance(val, (
            str,
            date,
            datetime
        ))

    def format(self, *args, **kwargs):

        args = list(map(
            lambda x: adapt(x) if SQL._must_escape(x) else x,
            args
        ))

        kwargs = dict(map(
            lambda x: (x[0], adapt(x[1])) if SQL._must_escape(x[1]) else (x[0], x[1]),
            kwargs.items()
        ))

        return SQL(super().format(*args, **kwargs))


class SQLTrustedString(SQL):
    """
    Represents a sql statement, expression or value
    which is safe to directly place inside a sql statement
    """
    pass
