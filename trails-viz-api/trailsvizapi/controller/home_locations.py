from flask import jsonify, Response

from trailsvizapi import app
from trailsvizapi.repository import home_locations


@app.route('/api/sites/<string:siteid>/source/<string:source>/homeLocations')
def get_home_locations(siteid, source):
    data = home_locations.get_home_locations(siteid, source)
    return jsonify(data)


@app.route('/api/sites/<string:siteid>/source/<string:source>/homeLocationsState')
def get_home_locations_state(siteid, source):
    data = home_locations.get_home_locations_by_state(siteid, source)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/source/<string:source>/homeLocationsCounty/<string:state_code>')
def get_home_locations_county(siteid, state_code, source):
    data = home_locations.get_home_locations_by_county(siteid, source, state_code)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/source/<string:source>/homeLocationsZCTA/<string:state_code>/<string:county_code>')
def get_home_locations_zcta(siteid, source, state_code, county_code):
    data = home_locations.get_home_locations_by_zcta(siteid, source, state_code, county_code)
    if data is None:
        return Response(status=204)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/homeLocationsCensusTract/<string:state_code>/<string:county_code>')
def get_home_locations_census_tract(siteid, state_code, county_code):
    data = home_locations.get_home_locations_by_census_tract(siteid, state_code, county_code)
    if data is None:
        return Response(status=204)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/projects/<string:project>/source/<string:source>/homeLocations')
def get_project_home_locations(project, source):
    data = home_locations.get_project_home_locations(project, source)
    return jsonify(data)


@app.route('/api/projects/<string:project>/source/<string:source>/homeLocationsState')
def get_project_home_locations_state(project, source):
    data = home_locations.get_project_home_locations_by_state(project, source)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/projects/<string:project>/source/<string:source>/homeLocationsCounty/<string:state_code>')
def get_home_project_locations_county(project, state_code, source):
    data = home_locations.get_project_home_locations_by_county(project, source, state_code)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/projects/<string:project>/source/<string:source>/homeLocationsZCTA/<string:state_code>/<string:county_code>')
def get_project_home_locations_zcta(project, source, state_code, county_code):
    data = home_locations.get_project_home_locations_by_zcta(project, source, state_code, county_code)
    if data is None:
        return Response(status=204)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/projects/<string:project>/homeLocationsCensusTract/<string:state_code>/<string:county_code>')
def get_project_home_locations_census_tract(project, state_code, county_code):
    data = home_locations.get_project_home_locations_by_census_tract(project, state_code, county_code)
    if data is None:
        return Response(status=204)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/source/<string:source>/homeLocationsDemographics')
def get_home_locations_demographics(siteid, source):
    data = home_locations.get_demographic_summary(siteid, source)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/projects/<string:project>/source/<string:source>/homeLocationsDemographics')
def get_project_home_locations_demographics(project, source):
    data = home_locations.get_project_demographic_summary(project, source)
    return Response(data.to_json(orient='records'), mimetype='application/json')
