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
        self.__token_table = config.get('token_table', 'users_tokens')

        super().__init__(config)

    def get_user(self, username):
        """
        Returns an user given an email
        """

        sql = 'SELECT * FROM {table} WHERE username = %s LIMIT 1;'.format(table=self.__user_table)

        res = self.query(sql, arguments=(username,), opts={'cache': False})
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
