"""
AUTH module
"""
import datetime
import logging

from functools import wraps
from flask import Blueprint, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from .config import cfg
from .models.usermodel import UserModel

def ini(app):
    log = logging.getLogger()

    JWTManager(app)
    EXPIRATION_DELTA = datetime.timedelta(seconds=cfg['AUTH_TOKEN_EXPIRATION'])
    app.config['JWT_TOKEN_LOCATION'] = 'headers'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = EXPIRATION_DELTA
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'JWT'
    # Algorithm used is SHA-256 hash
    # More info: https://pyjwt.readthedocs.io/en/latest/algorithms.html
    app.config['JWT_ALGORITHM'] = 'HS256'


routes =  Blueprint('auth', __name__)

def auth():
    """
    AUTH decorator. It checks for a valid token and validate this token against the DB
    """
    def decorator(func):
        """
        Decorator wrapper
        """
        @jwt_required
        @wraps(func)
        def check_token(*args, **kwargs):
            """
            Check token against DB
            """
            user_data = get_jwt_identity()
            token = request.headers.get('Authorization', None)
            if not token:
                return jsonify({'msg': 'You must provide authorization header (token)'}), 401

            if cfg['AUTH_TOKEN_DOBLE_CHECK']:
                user_model = UserModel({
                    'user_table' : cfg['AUTH_USER_TABLE'],
                    'token_table' : cfg['AUTH_TOKEN_TABLE']
                })
                valid = user_model.check_user_token(token)

                if not valid:
                    return jsonify({'msg': 'No valid token'}), 403

            request.user = user_data

            return func(*args, **kwargs)
        return check_token

    return decorator

@routes.route('/token', methods=['GET'])
def get_token():
    """
    Get a token given an user and password
    """
    username = request.headers.get('x-auth-username', None)
    password = request.headers.get('x-auth-password', None)

    if not username or not password:
        return jsonify({'msg': 'You must provide username and password'}), 401

    user_model = UserModel({
        'user_table' : cfg['AUTH_USER_TABLE'],
        'token_table' : cfg['AUTH_TOKEN_TABLE']
    })
    user_data = user_model.get_user(username)

    if not user_data or username != user_data['username'] or password != user_data['password']:
        return jsonify({'msg': 'Bad username or password'}), 401

    del user_data['password']

    request.user = user_data

    ret = {
        'token': 'JWT {0}'.format(create_access_token(identity=request.user)),
        'expiresIn': int(cfg['AUTH_TOKEN_EXPIRATION']),
        'user': request.user
    }

    if cfg['AUTH_TOKEN_DOBLE_CHECK']:
        upload_new_token(request.user.get('user_id'), ret['token'])

    return jsonify(ret), 200


@routes.route('/token/renew', methods=['GET'])
@auth()
def renew_token():
    """
    Create a new token
    """
    ret = {
        'token': 'JWT {0}'.format(create_access_token(identity=request.user)),
        'expires_in': int(cfg['AUTH_TOKEN_EXPIRATION']),
        'user': request.user
    }

    if cfg['AUTH_TOKEN_DOBLE_CHECK']:
        upload_new_token(request.user.get('id'), ret['token'])

    return jsonify(ret), 200


def upload_new_token(user_id, token):
    """
    Save a token into database
    """
    expiration_date = datetime.datetime.utcnow() + EXPIRATION_DELTA
    user_model = UserModel({
        'user_table' : cfg['AUTH_USER_TABLE'],
        'token_table' : cfg['AUTH_TOKEN_TABLE']
    })
    user_model.insert_user_token(user_id, token, expiration_date)
