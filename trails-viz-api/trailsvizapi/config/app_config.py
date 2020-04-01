import os

DATA_FILES_ROOT = os.getenv('DATA_FILES_ROOT', 'data-files/')
# Actual key must be set in the environment variable. This is just a placeholder
AUTH_TOKEN_KEY = os.getenv('AUTH_TOKEN_KEY', 'Some+Se3ret+Key+Placeholder+TrailsViz+01234=')
AUTH_BUCKET_NAME = 'recsetgo'

# if the project code contains the project group keyword, then it belongs to that group
PROJECT_NAMES = {
    'Western Washington': 'MBS_PIL',
    'Middle Fork': 'MBS_SARL',
    'Northern New Mexico': 'DOI_PIL',
    'King County Parks': 'KingCo'
}

CENSUS_TRACT_STATES = {
    'MBS_PIL': ['53'],
    'MBS_SARL': ['53'],
    'MBS_PIL, MBS_SARL': ['53'],
    'DOI_PIL': ['35'],
    'KingCo': ['53']
}

DATA_COLUMNS = {
    'MBS_PIL': ['estimate', 'flickr', 'twitter', 'instag', 'wta', 'onsite'],
    'MBS_SARL': ['estimate', 'flickr', 'twitter', 'instag', 'wta', 'onsite'],
    'DOI_PIL': ['estimate', 'flickr', 'twitter', 'instag', 'onsite'],
    'KingCo': ['flickr', 'twitter', 'instag', 'wta']
}
