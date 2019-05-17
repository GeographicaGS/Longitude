from psycopg2.extensions import string_types


def psycopg2_type_as_string(type_id):
    type_ = string_types.get(type_id)
    return type_.name if type_ else 'unknown'
