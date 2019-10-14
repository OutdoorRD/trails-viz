from flask import request, Response, jsonify

from trailsvizapi import app, data_repository, app_config


@app.route('/projects')
def get_all_projects():
    return jsonify(app_config.PROJECT_GROUPS)


@app.route('/sites/geojson')
def get_geojson_data():
    project_group = request.args.get('projectGroup')
    data = data_repository.get_project_sites(project_group)
    return Response(data.to_json(), mimetype='application/json')


@app.route('/sites/<int:siteid>/monthlyEstimates')
def get_monthly_estimates(siteid):
    data = data_repository.get_monthly_estimates(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/sites/<int:siteid>/annualEstimates')
def get_annual_estimates(siteid):
    data = data_repository.get_annual_estimates(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/sites/<int:siteid>/monthlyVisitation')
def get_monthly_visitation(siteid):
    data = data_repository.get_monthly_visitation(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/sites/<int:siteid>/weeklyVisitation')
def get_weekly_visitation(siteid):
    data = data_repository.get_weekly_visitation(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')
