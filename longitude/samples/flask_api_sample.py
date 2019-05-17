"""
██╗  ██╗ ██████╗ ██╗    ██╗    ████████╗ ██████╗     ██╗   ██╗███████╗███████╗    ████████╗██╗  ██╗██╗███████╗
██║  ██║██╔═══██╗██║    ██║    ╚══██╔══╝██╔═══██╗    ██║   ██║██╔════╝██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝██╗
███████║██║   ██║██║ █╗ ██║       ██║   ██║   ██║    ██║   ██║███████╗█████╗         ██║   ███████║██║███████╗╚═╝
██╔══██║██║   ██║██║███╗██║       ██║   ██║   ██║    ██║   ██║╚════██║██╔══╝         ██║   ██╔══██║██║╚════██║██╗
██║  ██║╚██████╔╝╚███╔███╔╝       ██║   ╚██████╔╝    ╚██████╔╝███████║███████╗       ██║   ██║  ██║██║███████║╚═╝
╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝        ╚═╝    ╚═════╝      ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝

Fill the needed environment variables using LONGITUDE__ as prefix!
"""

from pprint import pprint
from longitude.core.data_sources.postgres.default import PostgresDataSource
from longitude.core.rest_api.flask import LongitudeFlaskAPI as RESTApi
from longitude.samples.config import config

from marshmallow import Schema, fields


# Marshmallow schemas

class HomeSchema(Schema):
    debug_mode = config['debug']

    message = fields.String(default='')
    debug = fields.Boolean(default=debug_mode)

    # Conditional Schema (we show in the root the info if we are debugging)
    if debug_mode:
        data_sources = fields.Dict(keys=fields.Str(), values=fields.Str())


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
    @RESTApi.json_response(HomeSchema)
    def get(req):

        # As the schema shows data_sources info only if in debug, it is irrelevant if we fill it out here.
        return {
            'message': 'Api is running!',
            'data_sources': 'TODO, if necessary'
        }


class UsersManager:

    @staticmethod
    @RESTApi.json_response(UserSchema)
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
    @RESTApi.json_response(UserDetailSchema)
    def get(req):
        return {
            'id': req['user_id'],
            'details': 'Details of user with id %d' % req['user_id']
        }

    @staticmethod
    @RESTApi.json_response(UserDetailSchema)
    def post(req):
        return {
            'id': req['user_id'],
            'details': req.body['details']
        }


class UserManager:

    @staticmethod
    @RESTApi.json_response(UserSchema)
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
    data_sources = [PostgresDataSource({'user': 'user', 'password': 'userpass'})]
    schemas = [HomeSchema, GroupSchema, UserSchema, UserDetailSchema]
    managers = [UserManager, UsersManager, HomeManager]

    api = RESTApi(name='flask_api', options={
        'schemas': schemas,
        'managers': managers,
        'data_sources': data_sources
    })
    api.add_endpoint('/', manager=HomeManager)
    api.add_endpoint('/users', ['get', 'post'], manager=UsersManager)

    api.add_endpoint('/users/{user_id:Integer}', ['get', 'patch', 'delete'], manager=UserManager)
    api.add_endpoint('/users/{user_id:Integer}/details', {'get': UserDetailSchema, 'post': UserDetailSchema},
                     manager=UserDetailManager)

    if api.setup():
        pprint(api._spec.to_dict())
        api._app.run(debug=True)
