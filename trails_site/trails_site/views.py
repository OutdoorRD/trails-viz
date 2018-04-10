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
    #d = open(url_for('static', 'data/hikers_monthly.csv'))
    return jsonify(d.readlines())

@app.route('/api/annuals/<int:int>')
def get_annuals(int):
    filename = str(int) + '.csv'
    d = open(os.getcwd() + '/trails_site/static/data/annuals/' + filename)
    return jsonify(d.readlines())

@app.route('/api/monthlies/<int:int>')
def get_monthlies(int):
    filename = str(int) + '.csv'
    d = open(os.getcwd() + '/trails_site/static/data/monthlies/' + filename)
    return jsonify(d.readlines())
