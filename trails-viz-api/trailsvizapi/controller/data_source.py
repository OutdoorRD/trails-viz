from flask import Response
from trailsvizapi import app
from trailsvizapi.repository import data_source


@app.route('/api/datasources/<string:datasource>/readme')
def get_data_source_readme(datasource):
    data = data_source.get_data_source_readme(datasource)
    return Response(data, mimetype='text/markdown')
