from flask import Response

from trailsvizapi import app
from trailsvizapi.repository import visitation


@app.route('/api/projects/<string:project>/monthlyVisitation')
def get_project_monthly_visitation(project):
    data = visitation.get_project_monthly_visitation(project)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/projects/<string:project>/weeklyVisitation')
def get_project_weekly_visitation(project):
    data = visitation.get_project_weekly_visitation(project)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/sites/<int:siteid>/monthlyVisitation')
def get_monthly_visitation(siteid):
    data = visitation.get_monthly_visitation(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/sites/<int:siteid>/weeklyVisitation')
def get_weekly_visitation(siteid):
    data = visitation.get_weekly_visitation(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')

