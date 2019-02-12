import re
import json
from apispec.ext.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from flasgger import Swagger
from flask import Flask, request
from flask.wrappers import Response
from werkzeug.contrib.fixers import ProxyFix

from .base import LongitudeRESTAPI
from ..common.exceptions import LongitudeAppNotReady


class LongitudeFlaskAPI(LongitudeRESTAPI):
    _default_config = {
        'protocol': 'http',
        'host': 'localhost',
        'port': 5000,
        'debug': False,
        'secret': None,
        'allow_cors': True
    }
    plugins = (
        MarshmallowPlugin(),
        FlaskPlugin()
    )

    @classmethod
    def generate_json_response(cls, value, status_code=200):
        response = Response(
            response=json.dumps(value),
            status=status_code,
            mimetype='application/json'
        )
        return response

    def make_app(self):
        self._app = Flask(self.name)
        self._app.wsgi_app = ProxyFix(self._app.wsgi_app)
        self._app.debug = bool(self.get_config('debug'))
        self._app.secret_key = self.get_config('secret')
        if self.get_config('allow_cors'):
            from flask_cors import CORS
            CORS(self._app)

        # TODO Disable this from configuration if in production
        Swagger(self._app, template=self._spec.to_dict())

        with self._app.app_context():
            for ep in self._endpoints:
                for command in ep[1]:
                    name = command + '_' + ep[2].__name__.replace('Manager', '')

                    url = ep[0]
                    params_template = r"\{(\w+):(\w+)\}"
                    params = re.findall(params_template, url)
                    """
                    Converter types:
                        string 	(default) accepts any text without a slash
                        int 	accepts positive integers
                        float 	accepts positive floating point values
                        path 	like string but also accepts slashes
                        uuid 	accepts UUID strings
                    """
                    flask_param_type = {
                        'Integer': 'int'
                    }
                    for p in params:
                        api_parameter_string = '{%s:%s}' % (p[0], p[1])
                        flask_parameter_string = '<%s:%s>' % (flask_param_type[p[1]], p[0])
                        url = url.replace(api_parameter_string, flask_parameter_string)

                    self._app.add_url_rule(rule=url, endpoint=name, view_func=getattr(ep[2], command),
                                           methods=[command])
                    self._spec.add_path(ep[0], ep[1], view=getattr(ep[2], command))
        return self._app is not None

    def run(self):
        if self._app:
            self._app.run()
        else:
            raise LongitudeAppNotReady

    @staticmethod
    def get_request_body():
        return request.get_json(request.data)

    @staticmethod
    def get_request_query_params():
        return request.args

    @staticmethod
    def get_request_path_params():
        return request.view_args
