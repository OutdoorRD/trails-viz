import os

DATA_FILES_ROOT = os.getenv('DATA_FILES_ROOT', 'data-files/')
# Actual key must be set in the environment variable. This is just a placeholder
AUTH_TOKEN_KEY = os.getenv('AUTH_TOKEN_KEY', 'Some+Se3ret+Key+Placeholder+TrailsViz+01234=')
AUTH_BUCKET_NAME = 'recsetgo'

# if the project code contains the project group keyword, then it belongs to that group
PROJECT_NAMES = {
    'Western Washington': 'MBS_PIL',
    'Middle Fork': 'MBS_SARL',
    'Okanogan-Wenatchee Wilderness': 'OKW_WILD',
    'Okanogan-Wenatchee General Forest': 'OKW_GFA',
    'Northern New Mexico': 'DOI_PIL',
    'King County Parks': 'KingCo',
    'US National Forests Region 6' : 'ForestScale',
    'Mount Baker-Snoqualmie Wilderness': 'MBS_WILD'#,
    #'Mount Baker-Snoqualmie General Forest': 'MBS_GFA'
}

CENSUS_TRACT_STATES = {
    'MBS_PIL': ['53'],
    'MBS_SARL': ['53'],
    'OKW_WILD': ['53'],
    'OKW_GFA': ['53'],
    'MBS_PIL, MBS_SARL': ['53'],
    'DOI_PIL': ['35'],
    'KingCo': ['53'],
    'MBS_WILD': ['53']#,
    #'MBS_GFA': ['53']
}

DATA_COLUMNS = {
    'MBS_PIL': ['estimate', 'flickr', 'twitter', 'instag', 'wta', 'alltrails', 'onsite'],
    'MBS_SARL': ['estimate', 'flickr', 'twitter', 'instag', 'wta', 'alltrails', 'onsite'],
    'OKW_WILD': ['flickr', 'twitter', 'instag', 'wta'],
    'OKW_GFA': ['flickr', 'twitter', 'instag', 'wta'],
    'DOI_PIL': ['estimate', 'flickr', 'twitter', 'instag', 'onsite'],
    'KingCo': ['flickr', 'twitter', 'instag', 'wta'], 
    'ForestScale': ['flickr', 'twitter', 'instag', 'alltrails'],
    'MBS_WILD': ['estimate', 'flickr', 'twitter', 'instag', 'wta', 'alltrails']#,
    #'MBS_GFA': ['flickr', 'twitter', 'instag', 'wta', 'alltrails']
}
