from flask import Response
from trailsvizapi import app
from trailsvizapi.repository import party_characteristics


@app.route('/api/projects/<string:project>/partyCharacteristics')
def get_project_party_characteristics(project):
    data = party_characteristics.get_project_party_characteristics(project)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/sites/<string:siteid>/partyCharacteristics')
def get_party_characteristics(siteid):
    data = party_characteristics.get_party_characteristics(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')
