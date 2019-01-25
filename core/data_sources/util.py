import re


def is_write_query(sql_statement):
    """
    Check if a query string is a write query
    """
    write_cmds = 'drop|delete|insert|update|grant|execute|perform|create|begin|commit|alter'
    is_write = re.search(write_cmds, sql_statement.lower())
    return is_write
