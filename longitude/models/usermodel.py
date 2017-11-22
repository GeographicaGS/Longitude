"""
This module allows to manage an User in CARTO
"""
from .cartomodel import CartoModel
from .utils import SQL, SQLTrustedString

class UserModel(CartoModel):
    """
    UserModel class
    """
    def __init__(self, config={}):
        """
        Constructor
        """
        self.__user_table = config.get('user_table','users')
        self.__token_table = config.get('token_table','users_tokens')
        super(UserModel, self).__init__(config)

    def get_user(self, username):
        """
        Returns an user given an email
        """

        sql = SQL('''
            SELECT * FROM {table} WHERE username = {username} LIMIT 1;
        ''').format(
            table=SQLTrustedString(self.__user_table),
            username=username
        )

        res = self.query(sql, opts={'cache': False})
        if res:
            return res[0]

    def insert_user_token(self, user_id, token, expiration):
        """
        Insert a new  user_token
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
        Check uf an user token exists
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
        Delete an user token
        """

        sql = '''
            DELETE FROM {table} WHERE user_id = {user_id} AND expiration < now();
            '''.format(
                table=SQLTrustedString(self.__token_table),
                user_id=user_id
            )

        self.query(sql, opts={'write_qry': True})
