# from .trails_site import app

from flask import Flask, request, send_from_directory, jsonify
import json
import csv
app = Flask(__name__, static_url_path='')

import trails_site.views
