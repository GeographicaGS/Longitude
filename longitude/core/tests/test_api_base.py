from unittest import TestCase, mock

from longitude.core.rest_api.base import LongitudeRequest as Request
from longitude.core.rest_api.base import LongitudeRESTAPI as BaseApi

expected_default_return_error_codes = [400, 403, 404, 500]
expected_default_return_error_codes = ['default_%d' % c for c in expected_default_return_error_codes]

expected_default_return_codes = [200, 201, 202, 204]
expected_default_return_codes = ['default_%d' % c for c in expected_default_return_codes]


class FakeSchema:
    def __init__(self, many=False):
        pass

    @staticmethod
    def validate(value):
        if value == 'body ok':
            return []
        else:
            return [
                'something wrong'
            ]

    def dump(self, value):
        return value


class TestRequest(TestCase):
    def test_request_init(self):
        request = Request()
        self.assertIsNotNone(request)
        request.params = {'some_path_param': 'some_value'}
        self.assertIsNone(request['some_path_param_that_does_not_exist'])
        self.assertEqual('some_value', request['some_path_param'])


class TestRESTAPIBase(TestCase):
    def test_static_abstract_methods_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            BaseApi.generate_json_response(value=None)
        with self.assertRaises(NotImplementedError):
            BaseApi.get_request_body()
        with self.assertRaises(NotImplementedError):
            BaseApi.get_request_query_params()
        with self.assertRaises(NotImplementedError):
            BaseApi.get_request_path_params()
        with self.assertRaises(NotImplementedError):
            BaseApi.get_request_headers()

    def test_json_response_without_body(self):
        @BaseApi.json_response(FakeSchema)
        def fake_http_method(request):
            return 'generic data'

        with mock.patch('longitude.core.rest_api.base.LongitudeRESTAPI.generate_json_response') as fake_json_response:
            fake_json_response.return_value = 'Fake HTTP response'

            with mock.patch('longitude.core.rest_api.base.LongitudeRESTAPI.get_request') as fake_request:
                fake_request.return_value.body = None
                response = fake_http_method(Request())
                self.assertEqual('Fake HTTP response', response)

                fake_json_response.assert_called_once_with(value='generic data', status_code=200)

    def test_json_response_with_right_body(self):
        @BaseApi.json_response(FakeSchema)
        def fake_http_method(request):
            return 'generic data'

        with mock.patch('longitude.core.rest_api.base.LongitudeRESTAPI.generate_json_response') as fake_json_response:
            fake_json_response.return_value = 'Fake HTTP response'
            with mock.patch('longitude.core.rest_api.base.LongitudeRESTAPI.get_request') as fake_request:
                fake_request.return_value.body = 'body ok'
                response = fake_http_method(Request())
                self.assertEqual('Fake HTTP response', response)

                fake_json_response.assert_called_once_with(value='generic data', status_code=200)

    def test_json_response_with_wrong_body(self):
        @BaseApi.json_response(FakeSchema)
        def fake_http_method(request):
            return 'generic data'

        with mock.patch('longitude.core.rest_api.base.LongitudeRESTAPI.generate_json_response') as fake_json_response:
            fake_json_response.return_value = 'Fake HTTP response'
            with mock.patch('longitude.core.rest_api.base.LongitudeRESTAPI.get_request') as fake_request:
                fake_request.return_value.body = 'body not ok'
                response = fake_http_method(Request())
                self.assertEqual('Fake HTTP response', response)

                fake_json_response.assert_called_once_with(value={'errors': ['something wrong']}, status_code=400)

    def test_get_request(self):
        with self.assertRaises(NotImplementedError):
            BaseApi.get_request()

    def test_default_specification(self):
        api = BaseApi()
        self.assertIsNotNone(api)
        self.assertTrue(api.setup())

        specification = api.get_spec()
        self.assertIsNotNone(specification)

        self.assertEqual({}, specification['paths'])
        self.assertEqual('2.0', specification['swagger'])

        all_default_codes = expected_default_return_error_codes + expected_default_return_codes
        defined_default_codes = list(specification['definitions'].keys())
        self.assertCountEqual(all_default_codes, defined_default_codes)

        defined_errors = [specification['definitions'][c] for c in expected_default_return_error_codes]
        self.assertTrue(all([e['properties']['errors'] for e in defined_errors]))

    def test_add_schemas(self):
        with mock.patch('longitude.core.rest_api.base.APISpec.definition') as fake_add_definition_to_spec, mock.patch(
                'longitude.core.rest_api.base.APISpec.add_path') as fake_add_path:
            api = BaseApi(schemas=[FakeSchema])
            api._default_schemas = []  # So we can easily check the single call adding FakeSchema

            # Default get for root path (=index). As no IndexSchema is provided -> default_200
            api.add_endpoint(path='/')

            # As there is not ThingSchema defined -> default_200
            api.add_endpoint(path='/things', commands=['get', 'post'])

            # Here we can pass different schemas to different HTTP commands
            api.add_endpoint(path='/more_things', commands={'patch': FakeSchema, 'post': FakeSchema})

            # Here, as a FakeSchema is found, it will be used for the get command (default as no command is provided)
            api.add_endpoint(path='/fakes')

            api.setup()

            fake_add_definition_to_spec.assert_called_once_with('Fake', schema=FakeSchema)
            self.assertEqual(4, fake_add_path.call_count)
