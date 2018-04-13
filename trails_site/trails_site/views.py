from flask import Flask, request, send_from_directory, jsonify, url_for
import os
import json
import csv
from trails_site import app

@app.route('/')
def get_page():
    return app.send_static_file('index.html')

@app.route('/api/geojson')
def get_geojson():
    with open(os.getcwd() + '/trails_site/static/data/trails.geojson') as f:
        d = json.load(f)
    return jsonify(d)

@app.route('/api/hikers_monthly')
def get_hikersmonthly():
    d = open(os.getcwd() + '/trails_site/static/data/hikers_monthly.csv')
    fieldnames = ("AllTRLs_ID","date","predicted","actual","Trail_name")
    reader = csv.DictReader(d, fieldnames)
    next(reader)
    out = jsonify([row for row in reader])
    return out

@app.route('/api/annuals/<int:int>')
def get_annuals(int):
    filename = str(int) + '.csv'
    d = open(os.getcwd() + '/trails_site/static/data/annuals/' + filename)
    fieldnames = ("AllTRLs_ID","year","avg_pred")
    reader = csv.DictReader(d, fieldnames)
    next(reader)
    out = jsonify([row for row in reader])
    return out

@app.route('/api/monthlies/<int:int>')
def get_monthlies(int):
    filename = str(int) + '.csv'
    d = open(os.getcwd() + '/trails_site/static/data/monthlies/' + filename)
    fieldnames = ("AllTRLs_ID","month","avg_pred")
    reader = csv.DictReader(d, fieldnames)
    next(reader)
    out = jsonify([row for row in reader])
    return out
