from flask import Response
from trailsvizapi import app
from trailsvizapi.repository import party_characteristics
import json


@app.route('/api/projects/<string:project>/partyCharacteristics')
def get_project_party_characteristics(project):
    data = party_characteristics.get_project_party_characteristics(project)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/partyCharacteristics')
def get_party_characteristics(siteid):
    data = party_characteristics.get_party_characteristics(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/projects/<string:project>/partyCharacteristicsYearlyStatistics')
def get_project_party_characteristics_yearly_statistics(project):
    data = party_characteristics.get_project_party_characteristics_yearly_statistics(project)
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/partyCharacteristicsYearlyStatistics')
def get_party_characteristics_yearly_statistics(siteid):
    data = party_characteristics.get_party_characteristics_yearly_statistics(siteid)
    return Response(json.dumps(data), mimetype='application/json')
