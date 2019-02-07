from pprint import pprint
from longitude.core.rest_api.base import LongitudeRESTAPI

from marshmallow import Schema, fields

if __name__ == "__main__":
    class UserSchema(Schema):
        is_admin = fields.Boolean(default=False)
        username = fields.String(allow_none=False)
        first_name = fields.String(allow_none=False)
        last_name = fields.String(allow_none=False)


    schemas = [UserSchema]
    api = LongitudeRESTAPI(schemas=schemas)
    api.setup()
    api.add_path('/')
    api.add_path('/users', {'get': {'responses': {'200': {'schema': {'$ref': 'User'}}}}})
    pprint(api._spec.to_dict())
