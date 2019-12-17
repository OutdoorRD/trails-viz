import json

from flask import request, Response

from trailsvizapi import app

_ANON_AUTH_HEADER = 'anon'
_PROTECTED_ENDPOINTS = []


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
