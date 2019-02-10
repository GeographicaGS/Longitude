from pprint import pprint
from longitude.core.rest_api.flask import LongitudeFlaskAPI
from longitude.core.common.config import EnvironmentConfiguration as Config

from marshmallow import Schema, fields


# Marshmallow schemas

class HomeSchema(Schema):
    message = fields.String(default='')
    debug = fields.Boolean(default=bool(Config.get('flask_api.debug')))


class GroupSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()


class UserSchema(Schema):
    id = fields.Integer()
    is_admin = fields.Boolean(default=False)
    username = fields.String(allow_none=False)
    first_name = fields.String(allow_none=False, default='')
    last_name = fields.String(allow_none=False, default='')
    groups = fields.Nested(GroupSchema, only=('id', 'name'))


class UserDetailSchema(Schema):
    id = fields.Integer()
    details = fields.String(required=True)


# Views

class HomeManager:
    @staticmethod
    @LongitudeFlaskAPI.json_response(HomeSchema)
    def get(req):
        return {'message': 'Api is running!'}


class UsersManager:

    @staticmethod
    @LongitudeFlaskAPI.json_response(UserSchema)
    def get(req):
        return [
            {'id': 0,
             'is_admin': True,
             'username': 'admin'},
            {'id': 1,
             'is_admin': False,
             'username': 'test'}
        ]

    @staticmethod
    def post(req):
        pass


class UserDetailManager:
    @staticmethod
    @LongitudeFlaskAPI.json_response(UserDetailSchema)
    def get(req):
        return {
            'id': req['user_id'],
            'details': 'Details of user with id %d' % req['user_id']
        }

    @staticmethod
    @LongitudeFlaskAPI.json_response(UserDetailSchema)
    def post(req):
        return {
            'id': req['user_id'],
            'details': req.body['details']
        }


class UserManager:
    @staticmethod
    @LongitudeFlaskAPI.json_response(UserSchema)
    def get(req):
        user_id = req['user_id']
        return {
            'id': user_id,
            'is_admin': bool(user_id == 0),
            'username': 'user_' + str(user_id),
            'groups': []
        }

    @staticmethod
    def patch(req):
        pass

    @staticmethod
    def delete(req):
        pass


# App config

if __name__ == "__main__":
    schemas = [HomeSchema, GroupSchema, UserSchema, UserDetailSchema]
    managers = [UserManager, UsersManager, HomeManager]

    api = LongitudeFlaskAPI(config=Config.get('flask_api'), schemas=schemas, managers=managers)
    api.add_endpoint('/', manager=HomeManager)
    api.add_endpoint('/users', ['get', 'post'], manager=UsersManager)

    api.add_endpoint('/users/{user_id:Integer}', ['get', 'patch', 'delete'], manager=UserManager)
    api.add_endpoint('/users/{user_id:Integer}/details', {'get': UserDetailSchema, 'post': UserDetailSchema},
                     manager=UserDetailManager)

    api.setup()

    pprint(api._spec.to_dict())

    api._app.run(debug=True)
