from pprint import pprint
from longitude.core.rest_api.flask import LongitudeFlaskAPI
from longitude.core.common.config import EnvironmentConfiguration as Config

from marshmallow import Schema, fields


class HomeSchema(Schema):
    message = fields.String(default='Api is running!')


class HomeManager:
    @staticmethod
    def get():
        return HomeSchema().dumps({})


class GroupSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()


class UserSchema(Schema):
    id = fields.Integer()
    is_admin = fields.Boolean(default=False)
    username = fields.String(allow_none=False)
    first_name = fields.String(allow_none=False)
    last_name = fields.String(allow_none=False)
    groups = fields.Nested(GroupSchema, only=('id', 'name'))


class UserDetailSchema(Schema):
    details = fields.String()


class UsersManager:

    @staticmethod
    def get():
        pass

    @staticmethod
    def post():
        pass


class UserDetailManager:
    @staticmethod
    def get():
        pass

    @staticmethod
    def post():
        pass


class UserManager:
    @staticmethod
    def get():
        pass

    @staticmethod
    def patch():
        pass

    @staticmethod
    def delete():
        pass


if __name__ == "__main__":
    schemas = [HomeSchema, GroupSchema, UserSchema, UserDetailSchema]
    managers = [UserManager, UsersManager, HomeManager]

    api = LongitudeFlaskAPI(config=Config.get('flask_api'), schemas=schemas, managers=managers)
    api.add_endpoint('/', manager=HomeManager)
    api.add_endpoint('/users', ['get', 'post'], manager=UsersManager)
    api.add_endpoint('/users/{id:Integer}', ['get', 'patch', 'delete'], manager=UserManager)
    api.add_endpoint('/users/{id:Integer}/details', {'get': UserDetailSchema, 'post': UserDetailSchema},
                     manager=UserDetailManager)

    api.setup()

    pprint(api._spec.to_dict())

    api._app.run()
