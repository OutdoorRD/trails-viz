import os

DATA_FILES_ROOT = os.getenv('DATA_FILES_ROOT', 'data-files/')
# if the project code contains the project group keyword, then it belongs to that group
PROJECT_NAMES = {
    'Western Washington': 'MBS_PIL',
    'Middle Fork': 'MBS_SARL',
    'Northern New Mexico': 'DOI',
    'King County Parks': 'KingCo'
}

CENSUS_TRACT_STATES = {
    'MBS_PIL': ['53'],
    'MBS_SARL': ['53'],
    'MBS_PIL, MBS_SARL': ['53'],
    'DOI': ['35'],
    'KingCo': ['53']
}
