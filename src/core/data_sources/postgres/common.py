from psycopg2.extensions import string_types


def psycopg2_type_as_string(type_id):
    return string_types[type_id]
