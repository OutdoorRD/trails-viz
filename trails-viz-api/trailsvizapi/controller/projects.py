from flask import request, Response, jsonify

from trailsvizapi import app
from trailsvizapi.config import app_config
from trailsvizapi.repository import projects_and_sites


# @app.after_request
# def add_cors_headers(response):
#     response.headers["Access-Control-Allow-Origin"] = "http://localhost:8080"
#     response.headers["Access-Control-Allow-Headers"] = "Content-Type"
#     return response


@app.route('/api/projects')
def get_all_projects():
    return jsonify(app_config.PROJECT_NAMES)


@app.route('/api/projects/<string:project>/sites/geojson')
def get_geojson_data(project):
    data = projects_and_sites.get_project_sites(project)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/api/projects/<string:project>/readme')
def get_project_readme(project):
    readme_type = request.args.get('type')
    data = projects_and_sites.get_project_readme(readme_type, project)
    return Response(data, mimetype='text/markdown')


@app.route('/api/readme')
def get_readme():
    readme_type = request.args.get('type')
    data = projects_and_sites.get_project_readme(readme_type)
    return Response(data, mimetype='text/markdown')


@app.route('/api/projects/<string:project>/dataSources')
def get_project_data_sources(project):
    return jsonify(app_config.DATA_COLUMNS[project])
