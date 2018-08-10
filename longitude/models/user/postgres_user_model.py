"""
This module allows to manage an User in Postgres
"""
from longitude.models.base_models import PostgresModel
from longitude.models.user import AbstractUserModel


class PostgresUserModel(AbstractUserModel, PostgresModel):
    """
    PostgresUserModel class
    """

    def __init__(self, config={}):
        """
        Constructor
        """
        self.__user_table = config.get('user_table', 'users')
        self.__login_fields = config.get('auth_login_fields', 'username')
        self.__token_table = config.get('token_table', 'users_tokens')
        self.__last_access_field = config.get('last_access_field', 'last_access')
        super().__init__(config)

    def get_user(self, username):
        """
        Returns user data given a username, email or other login field
        """
        login_fields = self.__login_fields.split(',')
        where_clause = ' OR '.join(["{field} = '{username}'".format(field=x, username=username) for x in login_fields])

        sql = '''
            SELECT * FROM {table} WHERE {where_clause} LIMIT 1;
        '''.format(
            table=SQLTrustedString(self.__user_table),
            where_clause=where_clause
        )

        res = self.query(sql, opts={'cache': False})
        if res:
            return res[0]

    def insert_user_token(self, user_id, token, expiration):
        """
        Insert a new  user_token
        """

        sql = 'INSERT INTO {table} (user_id, token, expiration) VALUES (%s, %s::text, %s::timestamp);'.format(
            table=self.__token_table)

        self.query(sql, arguments=(user_id, token, expiration), opts={'write_qry': True, 'cache': False})

    def check_user_token(self, token):
        """
        Check uf an user token exists
        """

        sql = '''
            SELECT exists(
                SELECT 1 FROM {table}
                    WHERE token=%s::text
                )
            '''.format(table=self.__token_table)

        res = self.query(sql, arguments=(token,), opts={'cache': False})
        if res:
            return res[0]['exists']

    def delete_user_token(self, user_id):
        """
        Delete an user token
        """

        sql = '''
            DELETE FROM {table} WHERE user_id = %s AND expiration < now();
            '''.format(table=self.__token_table)

        self.query(sql, arguments=(user_id,), opts={'write_qry': True})

    def update_last_access(self, user_id):
        """
        Update Last Access field in Users table
        """

        sql = '''
            UPDATE {table} SET {last_access_field} = now() WHERE id = {user_id};
            '''.format(
            table=SQLTrustedString(self.__user_table),
            last_access_field=SQLTrustedString(self.__last_access_field),
            user_id=user_id
        )

        self.query(sql, opts={'write_qry': True})
