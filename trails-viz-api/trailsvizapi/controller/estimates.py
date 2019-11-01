from flask import Response

from trailsvizapi import app
from trailsvizapi.repository import estimates


@app.route('/api/sites/<int:siteid>/monthlyEstimates')
def get_monthly_estimates(siteid):
    data = estimates.get_monthly_estimates(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')


@app.route('/api/sites/<int:siteid>/annualEstimates')
def get_annual_estimates(siteid):
    data = estimates.get_annual_estimates(siteid)
    return Response(data.to_json(orient='records'), mimetype='application/json')
