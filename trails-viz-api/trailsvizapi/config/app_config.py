import os

DATA_FILES_ROOT = os.getenv('DATA_FILES_ROOT', 'data-files/')
# if the project code contains the project group keyword, then it belongs to that group
PROJECT_NAMES = {
    'Western Washington': 'MBS_PIL',
    'Middle Fork': 'MBS_SARL',
    'Northern New Mexico': 'DOI',
    'King County Parks': 'KingCo'
}
