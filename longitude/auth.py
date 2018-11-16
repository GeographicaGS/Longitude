"""
AUTH module
"""
import datetime
import logging
import bcrypt

from functools import wraps
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from .config import cfg
from .models.user_model import UserModel
from dateutil.parser import parse


EXPIRATION_DELTA = datetime.timedelta(seconds=cfg['AUTH_TOKEN_EXPIRATION'])


def ini(app):
    log = logging.getLogger()

    log.info(cfg['AUTH_TOKEN_EXPIRATION'])

    JWTManager(app)
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = EXPIRATION_DELTA
    app.config['JWT_HEADER_NAME'] = cfg['AUTH_HEADER_NAME']
    app.config['JWT_HEADER_TYPE'] = 'JWT'
    # Algorithm used is SHA-256 hash
    # More info: https://pyjwt.readthedocs.io/en/latest/algorithms.html
    app.config['JWT_ALGORITHM'] = 'HS256'


routes = Blueprint('auth', __name__)


def auth(allow_profiles=None, disallow_profiles=None):
    """AUTH decorator.

    It checks for a valid token and validates this token against the DB.

    With AUTH_USE_PROFILES env var activated it will aditionally check if
    the user has a allowed or disallowed profile for the endpoint.
    You can only specify a set of allowed profiles or a set of disallowed
    profiles.

    :param allow_profiles: A list of profiles/roles that can access \
                           the endpoint, defaults to None.
    :param allow_profiles: list[str], optional.
    :param disallow_profiles: A list of profiles/roles that cannot access \
                              the endpoint, defaults to None
    :param disallow_profiles: list[str], optional.
    :raises ValueError: If both allowed and disallowed profiles are specified.
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
            token = request.headers.get(cfg['AUTH_HEADER_NAME'], None)

            if not token:
                token = request.args.get('jwt')

            if not token:
                return jsonify({
                    'msg': 'You must provide an authorization header (token)'
                }), 401

            if cfg['AUTH_TOKEN_DOBLE_CHECK']:
                user_model = UserModel({
                    'user_table': cfg['AUTH_USER_TABLE'],
                    'token_table': cfg['AUTH_TOKEN_TABLE']
                })
                valid = user_model.check_user_token(token)

                if not valid:
                    return jsonify({'msg': 'No valid token'}), 403

            if cfg['AUTH_USE_PROFILES']:
                allow_type_prfs = check_auth_profiles(allow_profiles)
                disallow_type_prfs = check_auth_profiles(disallow_profiles)
                user_prof = user_data['profile']

                err_response = jsonify(
                    {
                        'msg': 'You are not authorized to request '
                        'this information'
                    }
                ), 403

                if (allow_type_prfs is list and
                        disallow_type_prfs is list):
                    raise ValueError('You can only specify allowed profiles '
                                     'or disallowed profiles')
                elif allow_type_prfs is list:
                    if user_prof not in allow_profiles:
                        return err_response
                elif disallow_type_prfs is list:
                    if user_prof in disallow_profiles:
                        return err_response

            request.user = user_data
            request.token = token

            return func(*args, **kwargs)

        return check_token

    return decorator


def check_login_fields(fields_list, user_data, username):
    check_list = [True for x in fields_list if user_data[x] == username]
    return True if check_list else False


def check_auth_profiles(profiles):
    correct = True
    prof_type = None

    if type(profiles) is list:
        prof_type = list
        if len(profiles):
            for element in profiles:
                if type(element) is not str:
                    correct = False
                    break
            prof_type = list if correct else None
    elif profiles is None:
        pass
    else:
        correct = False

    if not correct:
        raise ValueError('Profiles parameter is expected to be a list[str]')
    else:
        return prof_type


@routes.route('/token', methods=['GET'])
def get_token():
    """
    Get a token given a user and password
    """
    username = request.headers.get('x-auth-username', None)
    password = request.headers.get('x-auth-password', None)

    if not username or not password:
        return jsonify({'msg': 'You must provide username and password'}), 401

    user_model = UserModel({
        'user_table': cfg['AUTH_USER_TABLE'],
        'auth_login_fields': cfg['AUTH_LOGIN_FIELDS'],
        'token_table': cfg['AUTH_TOKEN_TABLE'],
        'last_access_field': cfg['AUTH_LAST_ACCESS_FIELD']
    })
    user_data = user_model.get_user(username)

    login_fields = cfg['AUTH_LOGIN_FIELDS'].split(',')

    if (not user_data or
        not check_login_fields(login_fields, user_data, username) or
        not bcrypt.checkpw(password.encode('utf8'),
                           user_data['password'].encode('utf-8'))):
        return jsonify({'msg': 'Bad username or password'}), 401

    if cfg['AUTH_ACCOUNT_EXPIRATION_FIELD']:
        exp = user_data[cfg['AUTH_ACCOUNT_EXPIRATION_FIELD']]
        if exp and parse(exp) < datetime.datetime.now(datetime.timezone.utc):
            return jsonify({'msg': 'This account has expired'}), 401

    if cfg['AUTH_UPDATE_LAST_ACCESS']:
        user_model.update_last_access(user_data['id'])

    if cfg['EXTRA_JWT_IDENTITY_FIELDS']:
        extra_jwt_identity_fields = {
            key.replace('JWT_IDENTITY_', '').lower(): value
            for (key, value) in
            cfg['EXTRA_JWT_IDENTITY_FIELDS'].items()
        }
        user_data.update(extra_jwt_identity_fields)

    del user_data['password']

    request.user = user_data

    ret = {
        'token': 'JWT {0}'.format(create_access_token(identity=request.user)),
        'expires_in': int(cfg['AUTH_TOKEN_EXPIRATION']),
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
        'user_table': cfg['AUTH_USER_TABLE'],
        'token_table': cfg['AUTH_TOKEN_TABLE']
    })
    user_model.insert_user_token(user_id, token, expiration_date)
