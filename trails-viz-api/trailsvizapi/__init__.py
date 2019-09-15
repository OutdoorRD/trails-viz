# version must be updated here, setup.py reads from this file
from flask import Flask

__version__ = '0.0.1'

app = Flask(__name__)

from trailsvizapi.controller import *
