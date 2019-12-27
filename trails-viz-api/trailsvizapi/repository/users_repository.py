import json

from google.api_core.exceptions import NotFound
from google.cloud import storage

AUTH_BUCKET_NAME = 'trails-viz-auth-test'
BUCKET_SOURCE = {}


# bucket reference is stored in a dict here for lazy loading
def _bucket_reference():
    if 'bucket' not in BUCKET_SOURCE:
        storage_client = storage.Client()
        bucket_name = AUTH_BUCKET_NAME
        BUCKET_SOURCE['bucket'] = storage_client.bucket(bucket_name)
    return BUCKET_SOURCE['bucket']


def create_update_user(username, user_json):
    bucket = _bucket_reference()
    user_json = json.dumps(user_json)
    blob = bucket.blob('users/' + username + '.json')
    blob.upload_from_string(data=user_json, content_type='application/json')


def get_user_json(username):
    bucket = _bucket_reference()
    blob = bucket.blob('users/' + username + '.json')
    try:
        obj = blob.download_as_string()
        return json.loads(obj)
    except NotFound:
        raise NameError('invalid username: {}'.format(username))


def list_users(prefix=None):
    prefix = 'users/' if prefix is None else 'users/' + prefix
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(AUTH_BUCKET_NAME, prefix=prefix)
    return [b.name.split('/')[1].split('.')[0] for b in blobs]
