import json
import uuid
from datetime import datetime

from cryptography.fernet import Fernet
from flask import request, Response

from trailsvizapi import app
from trailsvizapi.config import app_config

_ANON_AUTH_HEADER = 'anon'
_PROTECTED_ENDPOINTS = []

# configure the Fernet objects and auth token cache
_KEY = app_config.AUTH_TOKEN_KEY.encode()
_FERNET = Fernet(_KEY)
_AUTH_TOKENS_CACHE = dict()


def generate_auth_token(user_json):
    username = user_json['username']
    utc_now = datetime.timestamp(datetime.utcnow()) * 1000

    # the auth token structure is username random_uuid expiration_timestamp
    # expiration_timestamp is 24 hours from generation i.e. 24 * 60 * 60 * 1000 milliseconds
    auth_token = username + ' ' + uuid.uuid4().hex + ' ' + str(utc_now + 86400000)

    # auth token is encrypted and sent to the client
    auth_token = _FERNET.encrypt(auth_token.encode()).decode()

    return auth_token


def _validate_user(auth_header):
    return None, False


# Add authentication for each request. if this function doesn't return
# anything, it would mean that the request has been authenticated and authorized
@app.before_request
def authenticate_request():
    auth_header = request.headers.get('Authorization', default=_ANON_AUTH_HEADER)
    request_path = request.path
    endpoint = request.endpoint  # this would give the function name from the controller
    if auth_header == _ANON_AUTH_HEADER:
        if endpoint in _PROTECTED_ENDPOINTS:
            return Response(_unauthenticated_error_json(request_path), mimetype='application/json', status=401)
    else:
        user_name, authorized = _validate_user(auth_header)
        if not authorized:
            return Response(_unauthorized_error_json(user_name, request_path), mimetype='application/json', status=403)


def _unauthenticated_error_json(request_path):
    msg_dict = {
        'status': 401,
        'message': 'authentication required to access resource: {}'.format(request_path)
    }
    return json.dumps(msg_dict)


def _unauthorized_error_json(user, request_path):
    msg_dict = {
        'status': 403,
        'message': 'user {} not authorized to access resource: {}'.format(user, request_path)
    }
    return json.dumps(msg_dict)
