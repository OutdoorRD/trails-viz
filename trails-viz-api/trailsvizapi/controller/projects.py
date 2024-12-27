from flask import request, Response, jsonify

from trailsvizapi import app
from trailsvizapi.config import app_config
from trailsvizapi.repository import projects_and_sites
import geopandas as gpd #DAVID
import pandas as pd #DAVID
@app.route('/api/projects')
def get_all_projects():
    return jsonify(app_config.PROJECT_NAMES)


@app.route('/api/projects/<string:project>/sites/geojson')
def get_geojson_data(project):
    # Get the GeoDataFrame
    data = projects_and_sites.get_project_sites(project)

    # Multiply the size of the GeoDataFrame by 4
    if isinstance(data, gpd.GeoDataFrame):
        data = gpd.GeoDataFrame(pd.concat([data] * 4, ignore_index=True), crs=data.crs)
    else:
        # Handle non-GeoDataFrame cases, if necessary
        return Response("Unexpected data format", status=500, mimetype='text/plain')

    # Return the response as GeoJSON
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
