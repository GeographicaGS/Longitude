from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import Schema, fields
import inflect

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
    _inflect = inflect.engine()

    plugins = (
        MarshmallowPlugin(),
    )

    _DEFAULT_RESPONSES = {
        200: LongitudeOkResponseSchema,
        403: LongitudeNotAllowedResponseSchema,
        404: LongitudeNotFoundResponseSchema,
        500: LongitudeServerError
    }

    def __init__(self, name='Longitude Default REST API', version='0.0.1', return_code_defaults=None, schemas=None):
        self._spec: APISpec = None

        self.name = name
        self.version = version
        self.version = version

        self._schemas = schemas if schemas is not None else []

        # Defaults hold definitions for the common return codes as a dictionary
        self._default_schemas = return_code_defaults if return_code_defaults is not None else self._DEFAULT_RESPONSES

    def setup(self):
        self._spec = APISpec(
            title=self.name,
            version=self.version,
            openapi_version='2.0',
            plugins=self.plugins
        )

        for rc in self._default_schemas:
            self._spec.definition('default_%d' % rc, schema=self._default_schemas[rc])

        for sc in self._schemas:
            name = sc.__name__.replace('Schema', '')
            self._spec.definition(name, schema=sc)

    def add_path(self, path, commands=None):
        """

        :param path:
        :param commands: List of HTTP commands OR map of HTTP commands to Schemas
        :return:
        """
        if commands is None:  # By default, we assume it is get
            commands = ['get']

        # Mandatory response definitions that are not specified, are taken from the default ones
        operations = {}
        schema_names = [sc.__name__ for sc in self._schemas]
        for c in commands:
            operation = {'responses': {}}
            for response_code in self._DEFAULT_RESPONSES:
                ref = self._extract_description_reference(c, commands, path, response_code, schema_names)

                operation['responses'][str(response_code)] = {'schema': {'$ref': ref}}
            operations[c] = operation
            self._spec.add_path(path, operations)

    def _extract_description_reference(self, c, commands, path, response_code, schema_names):
        ref = 'default_%d' % response_code
        if response_code == 200:
            if isinstance(commands, dict):
                ref = commands[c].__name__
            else:
                schema_auto_name = self._inflect.singular_noun(path[1:]).capitalize() + 'Schema'
                if schema_auto_name in schema_names:
                    ref = schema_auto_name
        return ref
