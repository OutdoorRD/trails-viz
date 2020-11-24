# version must be updated here, setup.py reads from this file
from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt

__version__ = '2.8.0'

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

from trailsvizapi.config.auth import authenticate_request
from trailsvizapi.controller.projects import *
from trailsvizapi.controller.estimates import *
from trailsvizapi.controller.home_locations import *
from trailsvizapi.controller.visitation import *
from trailsvizapi.controller.users_controller import *
