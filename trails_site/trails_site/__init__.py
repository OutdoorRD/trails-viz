from flask import Flask, request, send_from_directory, jsonify
import json
import csv
app = Flask(__name__)

import trails_site.views
