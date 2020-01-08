import json
import uuid
from datetime import datetime

from cryptography.fernet import Fernet
from flask import request, Response

from trailsvizapi import app
from trailsvizapi.config import app_config

_ANON_AUTH_HEADER = 'anon'
_ANON_ENDPOINTS = {
    'get_all_projects',
    'get_geojson_data',
    'get_project_readme',
    'get_last_year_estimates',
    'get_readme',
    'get_project_data_sources',
    'get_monthly_estimates',
    'get_annual_estimates',
    'get_project_monthly_estimates',
    'get_project_annual_estimates',
    'get_project_monthly_visitation',
    'get_project_weekly_visitation',
    'get_monthly_visitation',
    'get_weekly_visitation',
    'authenticate_user'
}

_MANAGERS_ENDPOINTS = set(_ANON_AUTH_HEADER).update(
    'get_home_locations',
    'get_home_locations_state',
    'get_home_locations_county',
    'get_home_locations_census_tract',
    'get_project_home_locations',
    'get_project_home_locations_state',
    'get_home_project_locations_county',
    'get_project_home_locations_census_tract',
    'get_home_locations_demographics',
    'get_project_home_locations_demographics',
    'get_user',
    'add_update_user'
)

_ROLE_ACCESS_MAPPING = {
    'anon': _ANON_ENDPOINTS,
    'managers': _MANAGERS_ENDPOINTS
}

# configure the Fernet objects and auth token cache
_KEY = app_config.AUTH_TOKEN_KEY.encode()
_FERNET = Fernet(_KEY)


def generate_auth_token(user_json):
    username = user_json['username']
    role = user_json['role']
    utc_now = datetime.timestamp(datetime.utcnow()) * 1000
    rand = uuid.uuid4().hex

    # the auth token structure is username random_uuid expiration_timestamp
    # expiration_timestamp is 24 hours from generation i.e. 24 * 60 * 60 * 1000 milliseconds
    auth_token = username + ' ' + role + ' ' + rand + ' ' + str(utc_now + 86400000)

    # auth token is encrypted and sent to the client
    auth_token = _FERNET.encrypt(auth_token.encode()).decode()

    return auth_token


def _parse_auth_header(auth_header):
    auth_token = auth_header.split(':')[-1]
    auth_token = _FERNET.decrypt(auth_token.encode()).decode()
    username, role, _,  expiration = auth_token.split()
    return username, role, expiration


# Add authentication for each request. if this function doesn't return
# anything or returns None, it would mean that the request has been authenticated and authorized
@app.before_request
def authenticate_request():
    if request.method == 'OPTIONS':
        # return true for pre flight options requests by browser
        return

    endpoint = request.endpoint  # this would give the function name from the controller

    # if unprotected endpoint, allow execution without any auth header
    if endpoint in _ROLE_ACCESS_MAPPING['anon']:
        return

    auth_header = request.headers.get('Authorization', default=_ANON_AUTH_HEADER)
    request_path = request.path

    if auth_header == _ANON_AUTH_HEADER:
        if endpoint not in _ROLE_ACCESS_MAPPING['anon']:
            return Response(_unauthenticated_error_json(request_path), mimetype='application/json', status=401)

    username, role, expiration = _parse_auth_header(auth_header)
    utc_now = datetime.timestamp(datetime.utcnow()) * 1000
    if utc_now > float(expiration):
        return Response(_auth_token_expired_error_json(username), mimetype='application/json', status=401)

    # admins have access to every endpoint, allow access
    if role == 'admin':
        return

    # if using the user's endpoint, make sure non admins only have access to their user info
    if endpoint == 'get_user' or endpoint == 'add_update_user':
        path_username = request_path.split('/')[-1]
        if path_username != username:
            return Response(_unauthorized_error_json(username, request_path), mimetype='application/json', status=403)

    role_authorized_endpoints = _ROLE_ACCESS_MAPPING[role]
    if endpoint not in role_authorized_endpoints:
        return Response(_unauthorized_error_json(username, request_path), mimetype='application/json', status=403)


def _unauthenticated_error_json(request_path):
    msg_dict = {
        'status': 401,
        'message': 'authentication required to access resource: {}'.format(request_path)
    }
    return json.dumps(msg_dict)


def _auth_token_expired_error_json(user):
    msg_dict = {
        'status': 403,
        'message': 'user {}, auth token has expired. please login again'.format(user)
    }
    return json.dumps(msg_dict)


def _unauthorized_error_json(user, request_path):
    msg_dict = {
        'status': 403,
        'message': 'user {} not authorized to access resource: {}'.format(user, request_path)
    }
    return json.dumps(msg_dict)
