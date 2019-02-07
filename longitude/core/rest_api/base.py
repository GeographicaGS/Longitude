from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import Schema, fields


class LongitudeDefaultSchema(Schema):
    pass


class LongitudeOkResponseSchema(LongitudeDefaultSchema):
    payload = fields.Raw(default={})


class LongitudeNotFoundResponseSchema(LongitudeDefaultSchema):
    error = fields.String(default="Resource not found")


class LongitudeNotAllowedResponseSchema(LongitudeDefaultSchema):
    error = fields.String(default="Not authorized")


class LongitudeServerError(LongitudeDefaultSchema):
    error = fields.String(default="Internal server error. Contact support team.")


class LongitudeRESTAPI:
    plugins = (
        MarshmallowPlugin(),
    )

    _DEFAULT_RESPONSES = {
        200: LongitudeOkResponseSchema,
        404: LongitudeNotFoundResponseSchema,
        403: LongitudeNotAllowedResponseSchema,
        500: LongitudeServerError
    }

    def __init__(self, name='Longitude Default REST API', version='0.0.1', return_code_defaults=None, schemas=None):
        self._spec: APISpec = None

        self.name = name
        self.version = version
        self.version = version

        self._schemas = schemas if schemas is not None else []

        # Defaults hold definitions for the common return codes as a dictionary
        self._return_schemas = return_code_defaults if return_code_defaults is not None else self._DEFAULT_RESPONSES

    def setup(self):
        self._spec = APISpec(
            title=self.name,
            version=self.version,
            openapi_version='2.0',
            plugins=self.plugins
        )

        for rc in self._return_schemas:
            self._spec.definition('default_%d' % rc, schema=self._return_schemas[rc])

        for sc in self._schemas:
            name = sc.__name__.replace('Schema', '')
            self._spec.definition(name, schema=sc)

    def add_path(self, path, operations=None):

        if operations is None:
            operations = {'get': {}}
        # Mandatory response definitions that are not specified, are taken from the default ones
        for op in operations:
            operation = operations[op]
            if 'responses' not in operation.keys():
                operation['responses'] = {}
            for response_code in self._DEFAULT_RESPONSES:
                if str(response_code) not in operation['responses']:
                    operation['responses'][str(response_code)] = {'schema': {'$ref': 'default_%d' % response_code}}

            self._spec.add_path(path, operations)
