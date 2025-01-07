from trailsvizapi import app
from trailsvizapi.repository import chatbot_data


@app.route('/api/projects/<string:project>/chatbotData/<string:characteristic>')
def get_project_chatbot_data(project, characteristic):
    return chatbot_data.get_project_chatbot_data(project, characteristic)


@app.route('/api/sites/<string:siteid>/chatbotData/<string:characteristic>')
def get_chatbot_data(siteid, characteristic):
    return chatbot_data.get_chatbot_data(siteid, characteristic)


@app.route('/api/projects/<string:project>/chatbotDataYearlyStatistics/<string:characteristic>')
def get_project_chatbot_data_yearly_statistics(project, characteristic):
    return chatbot_data.get_project_chatbot_data_yearly_statistics(project, characteristic)


@app.route('/api/sites/<string:siteid>/chatbotDataYearlyStatistics/<string:characteristic>')
def get_chatbot_data_yearly_statistics(siteid, characteristic):
    return chatbot_data.get_chatbot_data_yearly_statistics(siteid, characteristic)
