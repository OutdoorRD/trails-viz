from flask import request, jsonify, Response

from trailsvizapi import app, bcrypt
from trailsvizapi.repository import users_repository


def _hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


@app.route('/api/users/<username>', methods=['POST'])
def add_update_user(username):
    user_json = request.get_json(silent=True)
    user_json['username'] = username
    password = user_json['password']
    password_hash = _hash_password(password)
    user_json['password'] = password_hash

    users_repository.create_update_user(username, user_json)
    del user_json['password']
    return jsonify(user_json)


@app.route('/api/users/<username>', methods=['GET'])
def get_user(username):
    try:
        user_json = users_repository.get_user_json(username)
        del user_json['password']
        return jsonify(user_json)
    except NameError as e:

        return Response('{"error": "' + e.args[0] + '"}', mimetype='application/json', status=404)


@app.route('/api/users/list/<string:prefix>', methods=['GET'])
def list_users(prefix):
    users_list = users_repository.list_users(prefix)
    return jsonify(users_list)
