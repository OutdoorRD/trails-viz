from flask import jsonify, Response

from trailsvizapi import app
from trailsvizapi.repository import home_locations


@app.route('/api/sites/<int:siteid>/homeLocations')
def get_home_locations(siteid):
    data = home_locations.get_home_locations(siteid)
    return jsonify(data)


@app.route('/api/projects/<string:project>/homeLocations')
def get_project_home_locations(project):
    data = home_locations.get_project_home_locations(project)
    return jsonify(data)


@app.route('/api/sites/censusTract')
def get_census_tract():
    data = home_locations.get_census_tract()
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/sites/<int:siteid>/homeLocationsCensusTract')
def get_home_locations_census_tract(siteid):
    data = home_locations.get_home_locations_by_census_tract(siteid)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/projects/<string:project>/homeLocationsCensusTract')
def get_project_home_locations_census_tract(project):
    data = home_locations.get_project_home_locations_by_census_tract(project)
    return Response(data.to_json(), mimetype='application/json')
