# version must be updated here, setup.py reads from this file
from flask import Flask
from flask_cors import CORS

__version__ = '0.0.1'

app = Flask(__name__)
CORS(app)

from trailsvizapi.controller.projects import *
from trailsvizapi.controller.estimates import *
from trailsvizapi.controller.home_locations import *
from trailsvizapi.controller.visitation import *
