from apispec.ext.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from flasgger import Swagger
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from .base import LongitudeRESTAPI


class LongitudeFlaskAPI(LongitudeRESTAPI):
    _default_config = {
        'debug': False,
        'secret': None,
        'allow_cors': True
    }
    plugins = (
        MarshmallowPlugin(),
        FlaskPlugin()
    )

    def make_app(self):
        self._app = Flask(self.name)
        self._app.wsgi_app = ProxyFix(self._app.wsgi_app)
        self._app.debug = bool(self.get_config('debug'))
        self._app.secret_key = self.get_config('secret')
        if self.get_config('allow_cors'):
            from flask_cors import CORS
            CORS(self._app)

        Swagger(self._app, template=self._spec.to_dict())

        with self._app.app_context():
            for ep in self._endpoints:
                for command in ep[1]:
                    name = command + '_' + ep[2].__name__.replace('Manager', '')
                    self._app.add_url_rule(ep[0], name, getattr(ep[2], command))
                    self._spec.add_path(ep[0], ep[1], view=getattr(ep[2], command))
