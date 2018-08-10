"""
This module allows to manage a User in CARTO
"""

from longitude.models.base_models import CartoModel
from longitude.models.user import AbstractUserModel
from longitude.models.utils import SQL, SQLTrustedString

class CartoUserModel(AbstractUserModel, CartoModel):
    """
    CartoUserModel class
    """

    def __init__(self, config={}):
        """
        Constructor
        """
        self.__user_table = config.get('user_table', 'users')
        self.__login_fields = config.get('auth_login_fields', 'username')
        self.__token_table = config.get('token_table', 'users_tokens')
        self.__last_access_field = config.get('last_access_field', 'last_access')
        super().__init__()

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
        Insert a new user_token
        """

        sql = SQL('''
            INSERT INTO {0}
                (user_id, token, expiration)
                VALUES ({1}, {2}::text, {3}::timestamp);
        ''').format(
            SQLTrustedString(self.__token_table),
            user_id,
            token,
            expiration
        )

        self.query(sql, opts={'write_qry': True, 'cache': False})

    def check_user_token(self, token):
        """
        Check if a user token exists
        """

        sql = '''
            SELECT exists(
                SELECT 1 FROM {0}
                    WHERE token='{1}'::text
                )
            '''.format(SQLTrustedString(self.__token_table), token)

        res = self.query(sql, opts={'cache': False})
        if res:
            return res[0]['exists']

    def delete_user_token(self, user_id):
        """
        Delete a user token
        """

        sql = '''
            DELETE FROM {table} WHERE user_id = {user_id} AND expiration < now();
            '''.format(
            table=SQLTrustedString(self.__token_table),
            user_id=user_id
        )

        self.query(sql, opts={'write_qry': True})

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
