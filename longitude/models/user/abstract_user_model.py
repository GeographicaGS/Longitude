from abc import ABC, abstractmethod


class AbstractUserModel(ABC):

    @abstractmethod
    def get_user(self, username):
        pass

    @abstractmethod
    def insert_user_token(self, user_id, token, expiration):
        pass

    @abstractmethod
    def check_user_token(self, token):
        pass

    @abstractmethod
    def delete_user_token(self, user_id):
        pass
