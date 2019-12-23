from flask import jsonify, Response

from trailsvizapi import app
from trailsvizapi.repository import home_locations


@app.route('/api/sites/<string:siteid>/homeLocations')
def get_home_locations(siteid):
    data = home_locations.get_home_locations(siteid)
    return jsonify(data)


@app.route('/api/sites/<string:siteid>/homeLocationsState')
def get_home_locations_state(siteid):
    data = home_locations.get_home_locations_by_state(siteid)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/homeLocationsCounty/<string:state_code>')
def get_home_locations_county(siteid, state_code):
    data = home_locations.get_home_locations_by_county(siteid, state_code)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/homeLocationsCensusTract/<string:state_code>/<string:county_code>')
def get_home_locations_census_tract(siteid, state_code, county_code):
    data = home_locations.get_home_locations_by_census_tract(siteid, state_code, county_code)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/projects/<string:project>/homeLocations')
def get_project_home_locations(project):
    data = home_locations.get_project_home_locations(project)
    return jsonify(data)


@app.route('/api/projects/<string:project>/homeLocationsState')
def get_project_home_locations_state(project):
    data = home_locations.get_project_home_locations_by_state(project)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/projects/<string:project>/homeLocationsCounty/<string:state_code>')
def get_home_project_locations_county(project, state_code):
    data = home_locations.get_project_home_locations_by_county(project, state_code)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/projects/<string:project>/homeLocationsCensusTract/<string:state_code>/<string:county_code>')
def get_project_home_locations_census_tract(project, state_code, county_code):
    data = home_locations.get_project_home_locations_by_census_tract(project, state_code, county_code)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/homeLocationsDemographics')
def get_home_locations_demographics(siteid):
    data = home_locations.get_demographic_summary(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/projects/<string:project>/homeLocationsDemographics')
def get_project_home_locations_demographics(project):
    data = home_locations.get_project_demographic_summary(project)
    return Response(data.to_json(orient='records'), mimetype='application/json')
