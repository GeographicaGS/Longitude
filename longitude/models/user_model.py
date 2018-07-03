"""
This module allows to manage a User in CARTO
"""
from .user import AbstractUserModel
from .user import CartoUserModel, PostgresUserModel
from longitude.config import cfg


class UserModel(AbstractUserModel):
    """
    UserModel class
    """

    def __init__(self, config={}):
        """
        Constructor
        """
        if cfg['DATABASE_MODEL'] == 'CARTO':
            self.base_model = CartoUserModel(config)
        elif cfg['DATABASE_MODEL'] == 'POSTGRES':
            self.base_model = PostgresUserModel(config)
        else:
            raise Exception('You need to specify a DATABASE_MODEL in environment variables')

        super().__init__()

    def get_user(self, username):
        """
        Returns a user given an email
        """

        return self.base_model.get_user(username)

    def insert_user_token(self, user_id, token, expiration):
        """
        Insert a new user_token
        """

        self.base_model.insert_user_token(user_id, token, expiration)

    def check_user_token(self, token):
        """
        Check if a user token exists
        """

        return self.base_model.check_user_token(token)

    def delete_user_token(self, user_id):
        """
        Delete a user token
        """

        self.base_model.delete_user_token(user_id)

    def update_last_access(self, user_id):

        """
        Update Last Access field in Users table
        """

        self.base_model.update_last_access(user_id)
