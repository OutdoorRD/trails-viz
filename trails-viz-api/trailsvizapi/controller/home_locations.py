from flask import jsonify

from trailsvizapi import app
from trailsvizapi.repository import home_locations


@app.route('/api/sites/<int:siteid>/homeLocations')
def get_home_locations(siteid):
    data = home_locations.get_home_locations(siteid)
    return jsonify(data)
