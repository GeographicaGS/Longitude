from apispec.ext.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin

from .base import LongitudeRESTAPI


class LongitudeFlaskAPI(LongitudeRESTAPI):
    plugins = (
        MarshmallowPlugin(),
        FlaskPlugin()
    )
