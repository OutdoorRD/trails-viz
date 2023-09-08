import os

DATA_FILES_ROOT = os.getenv('DATA_FILES_ROOT', 'data-files/')
# Actual key must be set in the environment variable. This is just a placeholder
AUTH_TOKEN_KEY = os.getenv('AUTH_TOKEN_KEY', 'Some+Se3ret+Key+Placeholder+TrailsViz+01234=')
AUTH_BUCKET_NAME = 'recsetgo'

# if the project code contains the project group keyword, then it belongs to that group
PROJECT_NAMES = {
    'West Cascades': 'WestCascades',
    'Middle Fork': 'WestCascades_MiddleFork',
    # 'Okanogan-Wenatchee Wilderness (Archived)': 'OKW_WILD',
    # 'Okanogan-Wenatchee General Forest (Archived)': 'OKW_GFA',
    'Northern New Mexico': 'NNM',
    'King County Parks': 'KingCo',
    'US National Forests': 'NationalForests',
    'Mount Baker-Snoqualmie Wilderness': 'MBS_WILD',
    'Mountain Loop': 'WestCascades_MtnLoop',
    'South Mountain Loop': 'WestCascades_SMtnLoop',
    # 'Mount Baker-Snoqualmie General Forest': 'MBS_GFA'
    'East Cascades': 'EastCascades',
    'Coronado': 'Coronado',
    'Bridger-Teton': 'BT'
}

CENSUS_TRACT_STATES = {
    'WestCascades': ['53'],
    'WestCascades_MiddleFork': ['53'],
    # 'OKW_WILD': ['53'],
    # 'OKW_GFA': ['53'],
    'NNM': ['35'],
    'KingCo': ['53'],
    'MBS_WILD': ['53'],
    'WestCascades_MtnLoop': ['53'],
    'WestCascades_SMtnLoop': ['53'],
    # 'MBS_GFA': ['53']
    'EastCascades': ['53']
}

DATA_COLUMNS = {
    'WestCascades': ['estimate', 'flickr', 'twitter', 'instag', 'wta', 'alltrails', 'onsite'],
    'WestCascades_MiddleFork': ['estimate', 'flickr', 'twitter', 'instag', 'wta', 'alltrails', 'onsite'],
    # 'OKW_WILD': ['flickr', 'twitter', 'instag', 'wta'],
    # 'OKW_GFA': ['flickr', 'twitter', 'instag', 'wta'],
    'NNM': ['estimate', 'flickr', 'twitter', 'instag', 'onsite'],
    'KingCo': ['flickr', 'twitter', 'instag', 'wta'],
    'NationalForests': ['flickr', 'twitter', 'instag', 'alltrails'],
    'MBS_WILD': ['estimate', 'flickr', 'twitter', 'instag', 'wta', 'alltrails'],
    'WestCascades_MtnLoop': ['estimate', 'flickr', 'twitter', 'instag', 'alltrails', 'ebird', 'wta', 'onsite'],
    'WestCascades_SMtnLoop': ['estimate', 'flickr', 'twitter', 'instag', 'alltrails', 'ebird', 'wta', 'onsite'],
    # 'MBS_GFA': ['flickr', 'twitter', 'instag', 'wta', 'alltrails']
    'EastCascades': ['estimate', 'flickr', 'twitter', 'alltrails', 'ebird', 'wta', 'onsite'],
    'Coronado': ['estimate', 'flickr', 'twitter', 'alltrails', 'ebird', 'onsite'],
    'BT': ['flickr', 'twitter', 'alltrails', 'ebird', 'gravy', 'onsite']
}
