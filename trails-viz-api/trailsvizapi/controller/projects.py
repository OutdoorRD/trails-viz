from flask import request, Response, jsonify

from trailsvizapi import app, app_config
from trailsvizapi.repository import projects_and_sites


@app.route('/api/projects')
def get_all_projects():
    return jsonify(app_config.PROJECT_NAMES)


@app.route('/api/sites/geojson')
def get_geojson_data():
    project_group = request.args.get('projectGroup')
    data = projects_and_sites.get_project_sites(project_group)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/projects/<string:project>/readme')
def get_project_readme(project):
    data = projects_and_sites.get_project_readme(project)
    return Response(data, mimetype='text/markdown')


@app.route('/api/readme')
def get_readme():
    readme_type = request.args.get('type')
    data = projects_and_sites.get_project_readme(readme_type)
    return Response(data, mimetype='text/markdown')
