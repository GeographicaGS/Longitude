import re
from math import floor

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from longitude.core.common.config import LongitudeConfigurable
from longitude.core.common.schemas import *
import inflect


class LongitudeRequest:
    def __init__(self):
        self.body = None
        self.query = None
        self.params = None

    def __getitem__(self, key):
        try:
            return self.params[key]
        except KeyError:
            return None


class LongitudeRESTAPI(LongitudeConfigurable):
    _inflect = inflect.engine()

    plugins = (
        MarshmallowPlugin(),
    )

    _DEFAULT_RESPONSES = {
        200: LongitudeOkResponseSchema,
        201: LongitudeCreated,
        202: LongitudeAccepted,
        204: LongitudeEmptyContent,
        403: LongitudeNotAllowedResponseSchema,
        404: LongitudeNotFoundResponseSchema,
        500: LongitudeServerError,
    }

    _DEFAULT_COMMAND_RESPONSES = {
        'get': [200, 403, 500],
        'post': [201, 403, 500],
        'delete': [204, 403, 500],
        'patch': [202, 403, 500]
    }

    @classmethod
    def generate_json_response(cls, value, status_code=200):
        raise NotImplementedError

    @classmethod
    def json_response(cls, response_schema_class, request_body_schema_class=None):
        # TODO: For now we are assuming that body requests have the same schema as the responses
        #  We can choose which fields are mandatory to validate the body schema

        request_body_schema_class = request_body_schema_class or response_schema_class

        def method_decorator(method):
            def wrapper(*args, **kwargs):
                request = cls.get_request()

                errors = []
                if request.body:
                    errors = request_body_schema_class().validate(request.body)

                if len(errors) == 0:
                    value = method(request)
                    is_list = isinstance(value, list) or isinstance(value, set) or isinstance(value, tuple)
                    data = response_schema_class(many=is_list).dump(value)
                    return cls.generate_json_response(value=data, status_code=200)
                else:
                    return cls.generate_json_response(value={'errors': errors}, status_code=400)

            return wrapper

        return method_decorator

    @staticmethod
    def get_request_body():
        raise NotImplementedError

    @staticmethod
    def get_request_query_params():
        raise NotImplementedError

    @staticmethod
    def get_request_path_params():
        raise NotImplementedError

    @classmethod
    def get_request(cls):
        req = LongitudeRequest()
        req.body = cls.get_request_body()
        req.query = cls.get_request_query_params()
        req.params = cls.get_request_path_params()
        return req

    def __init__(self, config=None, name='Longitude Default REST API', version='0.0.1', return_code_defaults=None,
                 schemas=None, managers=None):

        super().__init__(config)
        self._app = None
        self._spec: APISpec = None

        self.name = name
        self.version = version
        self.version = version

        self._schemas = schemas if schemas is not None else []
        self._managers = managers if managers is not None else []
        # Defaults hold definitions for the common return codes as a dictionary
        self._default_schemas = return_code_defaults if return_code_defaults is not None else self._DEFAULT_RESPONSES

        self._endpoints = []

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

        self.make_app()

    def make_app(self):
        for endpoint in self._endpoints:
            self._spec.add_path(endpoint[0], endpoint[1])

    def add_endpoint(self, path, commands=None, manager=None):
        """

        :param path:
        :param commands: List of HTTP commands OR map of HTTP commands to Schemas
        :param manager: Class defining methods for each HTTP command
        :return:
        """

        def parse_path(url_path):
            params_template = r"\{(\w+):(\w+)\}"
            if url_path == '/':
                auto_name = 'Home'
            else:
                name = url_path.split('/')[1]
                auto_name = self._inflect.singular_noun(name).capitalize()

            params = re.findall(params_template, url_path)
            return auto_name, params

        if commands is None:  # By default, we assume it is get
            commands = ['get']

        # Mandatory response definitions that are not specified, are taken from the default ones
        operations = {}
        schema_names = [sc.__name__ for sc in self._schemas]
        for c in commands:
            operation = {'responses': {}}
            for response_code in self._DEFAULT_COMMAND_RESPONSES[c]:
                ref = 'default_%d' % response_code
                if floor(response_code / 100) == 2:
                    if isinstance(commands, dict):
                        ref = commands[c].__name__.replace('Schema', '')
                    else:
                        auto_name, path_params = parse_path(path)
                        # TODO: spec forthe path_params
                        if auto_name + 'Schema' in schema_names:
                            ref = auto_name

                operation['produces'] = ['application/json']
                operation['responses'][str(response_code)] = {
                    'description': '',
                    'schema': {
                        '$ref': '#/definitions/%s' % ref
                    }
                }
                operations[c] = operation
        self._endpoints.append((path, operations, manager))

    def run(self):
        raise NotImplementedError
