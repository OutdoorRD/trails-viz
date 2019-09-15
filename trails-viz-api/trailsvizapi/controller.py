from flask import request, Response

from trailsvizapi import app, data_repository


@app.route('/api/geojson')
def get_geojson_data():
    project_group = request.args.get('projectGroup')
    data = data_repository.get_project_sites(project_group)
    return Response(data.to_json(), mimetype='application/json')
