from flask import Response

from trailsvizapi import app
from trailsvizapi.repository import party_characteristics


@app.route('/api/projects/<string:project>/partyPeople')
def get_project_party_people(project):
    data = party_characteristics.get_project_party_people(project)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/projects/<string:project>/partyVehicles')
def get_project_party_vehicles(project):
    data = party_characteristics.get_project_party_vehicles(project)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/projects/<string:project>/trailVisits')
def get_project_trail_visits(project):
    data = party_characteristics.get_project_trail_visits(project)
    return Response(data.to_json(orient='records'), mimetype='application/json')

@app.route('/api/projects/<string:project>/partyCharacteristics')
def get_project_party_characteristics(project):
    data = party_characteristics.get_project_party_characteristics(project)
    return Response(data.to_json(orient='records'), mimetype='application/json')

@app.route('/api/sites/<string:siteid>/partyPeople')
def get_party_people(siteid):
    data = party_characteristics.get_party_people(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/partyVehicles')
def get_party_vehicles(siteid):
    data = party_characteristics.get_party_vehicles(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/trailVisits')
def get_trail_visits(siteid):
    data = party_characteristics.get_trail_visits(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')

@app.route('/api/sites/<string:siteid>/partyCharacteristics')
def get_party_characteristics(siteid):
    data = party_characteristics.get_party_characteristics(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')