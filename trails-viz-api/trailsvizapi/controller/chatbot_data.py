from flask import request
from trailsvizapi import app
from trailsvizapi.repository import chatbot_data


@app.route('/api/projects/<string:project>/chatbotData/<string:characteristic>')
def get_project_chatbot_data(project, characteristic):
    year_start = request.args.get('year_start')
    year_end = request.args.get('year_end')
    return chatbot_data.get_project_chatbot_data(project, characteristic, year_start, year_end)


@app.route('/api/sites/<string:siteid>/chatbotData/<string:characteristic>')
def get_chatbot_data(siteid, characteristic):
    year_start = request.args.get('year_start')
    year_end = request.args.get('year_end')
    return chatbot_data.get_chatbot_data(siteid, characteristic, year_start, year_end)


@app.route('/api/projects/<string:project>/chatbotDataYearlyStatistics/<string:characteristic>')
def get_project_chatbot_data_yearly_statistics(project, characteristic):
    year_start = request.args.get('year_start')
    year_end = request.args.get('year_end')
    return chatbot_data.get_project_chatbot_data_yearly_statistics(project, characteristic, year_start, year_end)


@app.route('/api/sites/<string:siteid>/chatbotDataYearlyStatistics/<string:characteristic>')
def get_chatbot_data_yearly_statistics(siteid, characteristic):
    year_start = request.args.get('year_start')
    year_end = request.args.get('year_end')
    return chatbot_data.get_chatbot_data_yearly_statistics(siteid, characteristic, year_start, year_end)
