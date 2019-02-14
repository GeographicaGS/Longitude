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
    _default_config = {
        'host': 'localhost',
        'port': 80,
        'protocol': 'http'
    }

    _DEFAULT_RESPONSES = {
        200: LongitudeOkResponseSchema,
        201: LongitudeCreated,
        202: LongitudeAccepted,
        204: LongitudeEmptyContent,
        400: LongitudeBadRequest,
        403: LongitudeNotAllowedResponseSchema,
        404: LongitudeNotFoundResponseSchema,
        500: LongitudeServerError,
    }

    _DEFAULT_COMMAND_RESPONSES = {
        'get': [200, 403, 404, 500],
        'post': [201, 400, 403, 500],
        'delete': [204, 403, 404, 500],
        'patch': [202, 400, 403, 404, 500]
    }

    @classmethod
    def generate_json_response(cls, value, status_code=200):
        raise NotImplementedError

    @classmethod
    def json_response(cls, response_schema_class, request_body_schema_class=None):
        """
        This decorator is used to mark a function as API endpoint returning JSON data.

        :param response_schema_class: Marshmallow schema representing a valid response object.
        :param request_body_schema_class: Marshmallow schema representing a valid body request object (if needed)
        :return: HTTP Response with application/json Content-Type
        """
        # TODO: For now we are assuming that body requests have the same schema as the responses
        #  We can choose which fields are mandatory to validate the body schema to filter responses/requests

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

    @staticmethod
    def get_request_headers():
        raise NotImplementedError

    @classmethod
    def get_request(cls):
        req = LongitudeRequest()
        req.body = cls.get_request_body()
        req.query = cls.get_request_query_params()
        req.params = cls.get_request_path_params()
        return req

    def __init__(self, config='', title='Longitude Default REST API', version='0.0.1', return_code_defaults=None,
                 schemas=None, managers=None, data_sources=None):

        super().__init__(config=config)
        self._app = None
        self._spec: APISpec = None

        self.name = config
        self.title = title
        self.version = version
        self.version = version

        self._schemas = schemas if schemas is not None else []
        self._managers = managers if managers is not None else []
        self._data_sources = data_sources if data_sources is not None else []

        # Defaults hold definitions for the common return codes as a dictionary
        self._default_schemas = return_code_defaults if return_code_defaults is not None else self._DEFAULT_RESPONSES

        self._endpoints = []

    # TODO: If this class survives to hapic, we must remove the setup method as part of the interface and rely only
    #  on the is_ready thing
    def setup(self):

        options = {
            'host': "%s:%d" % (self.get_config('host'), self.get_config('port')),
            'schemas': [self.get_config('protocol')],
            'basePath': ''
        }

        self._spec = APISpec(
            title=self.title,
            version=self.version,
            openapi_version='2.0',
            plugins=self.plugins,
            **options
        )

        for rc in self._default_schemas:
            self._spec.definition('default_%d' % rc, schema=self._default_schemas[rc])

        for sc in self._schemas:
            name = sc.__name__.replace('Schema', '')
            self._spec.definition(name, schema=sc)

        data_sources_ok = all([ds.is_ready for ds in self._data_sources])

        return data_sources_ok and self.make_app()

    def make_app(self):
        """
        Derived classes must define its own method where the service app is created (Flask, bottle, Django...). The
        reference to the app must be stored at self._app

        In the base class, only endpoints are being defined here in an agnostic way.

        :return: Always True in base class. In derived class, it must return True if the app has been correctly created.
        """
        for endpoint in self._endpoints:
            self._spec.add_path(endpoint[0], endpoint[1])
        return True

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

        def _append_operation(http_command, operation, operations, ref, response_code):
            operation['produces'] = ['application/json']
            operation['responses'][str(response_code)] = {
                'description': '',
                'schema': {
                    '$ref': '#/definitions/%s' % ref
                }
            }
            operations[http_command] = operation

        def _generate_reference_name(http_command, commands, parse_path, path, response_code, schema_names):
            ref = 'default_%d' % response_code
            if floor(response_code / 100) == 2:
                if isinstance(commands, dict):
                    ref = commands[http_command].__name__.replace('Schema', '')
                else:
                    auto_name, path_params = parse_path(path)
                    # TODO: spec forthe path_params
                    if auto_name + 'Schema' in schema_names:
                        ref = auto_name
            return ref

        if commands is None:  # By default, we assume it is get
            commands = ['get']

        # Mandatory response definitions that are not specified, are taken from the default ones
        operations = {}
        schema_names = [sc.__name__ for sc in self._schemas]
        for c in commands:
            operation = {'responses': {}}
            for response_code in self._DEFAULT_COMMAND_RESPONSES[c]:
                reference_name = _generate_reference_name(c, commands, parse_path, path, response_code, schema_names)
                _append_operation(c, operation, operations, reference_name, response_code)
        self._endpoints.append((path, operations, manager))

    def run(self):
        raise NotImplementedError

    def get_spec(self):
        """
        Generated APISpec.
        :return: Returns the API specification as dictionary.
        """
        return self._spec.to_dict()
