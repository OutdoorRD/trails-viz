from trailsvizapi import app
from trailsvizapi.repository import party_characteristics


@app.route('/api/projects/<string:project>/partyCharacteristics/<string:characteristic>')
def get_project_party_characteristics(project, characteristic):
    return party_characteristics.get_project_party_characteristics(project, characteristic)


@app.route('/api/sites/<string:siteid>/partyCharacteristics/<string:characteristic>')
def get_party_characteristics(siteid, characteristic):
    return party_characteristics.get_party_characteristics(siteid, characteristic)


@app.route('/api/projects/<string:project>/partyCharacteristicsYearlyStatistics/<string:characteristic>')
def get_project_party_characteristics_yearly_statistics(project, characteristic):
    return party_characteristics.get_project_party_characteristics_yearly_statistics(project, characteristic)


@app.route('/api/sites/<string:siteid>/partyCharacteristicsYearlyStatistics/<string:characteristic>')
def get_party_characteristics_yearly_statistics(siteid, characteristic):
    return party_characteristics.get_party_characteristics_yearly_statistics(siteid, characteristic)
