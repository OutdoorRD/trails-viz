from flask import request, abort
from trailsvizapi import app
from trailsvizapi.repository import categorical_chatbot_data


@app.route('/api/projects/<string:project>/categoricalChatbotData/<string:characteristic>')
def get_project_categorical_chatbot_data(project, characteristic):
    year_start = request.args.get('year_start')
    year_end = request.args.get('year_end')
    try:
        year_start = int(year_start)
        year_end = int(year_end)
    except (ValueError, TypeError):
        abort(400, "Must provide integer year_start and year_end")
    return categorical_chatbot_data.get_project_categorical_chatbot_data(project, characteristic, year_start, year_end)


@app.route('/api/sites/<string:siteid>/categoricalChatbotData/<string:characteristic>')
def get_categorical_chatbot_data(siteid, characteristic):
    year_start = request.args.get('year_start')
    year_end = request.args.get('year_end')
    try:
        year_start = int(year_start)
        year_end = int(year_end)
    except (ValueError, TypeError):
        abort(400, "Must provide integer year_start and year_end")
    return categorical_chatbot_data.get_categorical_chatbot_data(siteid, characteristic, year_start, year_end)
