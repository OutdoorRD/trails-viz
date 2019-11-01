from flask import request, Response, jsonify

from trailsvizapi import app, app_config
from trailsvizapi.repository import sites


@app.route('/api/projects')
def get_all_projects():
    return jsonify(app_config.PROJECT_GROUPS)


@app.route('/api/sites/geojson')
def get_geojson_data():
    project_group = request.args.get('projectGroup')
    data = sites.get_project_sites(project_group)
    return Response(data.to_json(), mimetype='application/json')
