from flask import Response
from trailsvizapi import app
from trailsvizapi.repository import map_chatbots
import json


@app.route('/api/projects/<string:project>/get_annual_chatbot_response_counts')
def get_annual_chatbot_response_counts(project):
    data = map_chatbots.get_annual_chatbot_response_counts(project)
    return Response(json.dumps(data), mimetype='application/json')
