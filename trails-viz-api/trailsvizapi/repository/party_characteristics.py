import numpy as np
import geopandas as gpd
from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.projects_and_sites import get_project_sites

def _get_project_party_characteristics_data(project):
    project_sites = get_project_sites(project)
    party_characteristics_df = get_from_data_source('PARTY_CHARACTERISTICS_DF')
    siteids = set(project_sites['siteid'].unique())
    # Add a new column in df_vic_siteid called trail that contains the project site ids (None if observation is not part of project siteids)
    party_characteristics_df.loc[:,'trail'] = party_characteristics_df['SiteID'].apply(lambda lst: next((x for x in lst if x in siteids), None))
    party_characteristics_df = party_characteristics_df.dropna(subset=['trail'])
    return party_characteristics_df

def _get_party_characteristics_data(siteid):
    party_characteristics_df = get_from_data_source('PARTY_CHARACTERISTICS_DF')
    site_data = party_characteristics_df[party_characteristics_df['SiteID'].apply(lambda x: siteid in x)]
    site_data['trail'] = siteid
    return site_data

def get_project_party_people(project):
    return _get_project_party_characteristics_data(project)[['PartyPeople', 'trail']].dropna(subset=['PartyPeople'])

def get_project_party_vehicles(project):
    return _get_project_party_characteristics_data(project)[['PartyVehics', 'trail']].dropna(subset=['PartyVehics'])

def get_project_trail_visits(project):
    return _get_project_party_characteristics_data(project)[['TrailVisits', 'trail']].dropna(subset=['TrailVisits'])

def get_project_party_characteristics(project):
    return _get_project_party_characteristics_data(project)[['TrailVisits', 'PartyPeople','PartyVehics', 'trail']]

def get_party_people(siteid):
    return _get_party_characteristics_data(siteid)[['PartyPeople', 'trail']].dropna(subset=['PartyPeople'])

def get_party_vehicles(siteid):
    return _get_party_characteristics_data(siteid)[['PartyVehics', 'trail']].dropna(subset=['PartyVehics'])

def get_trail_visits(siteid):
    return _get_party_characteristics_data(siteid)[['TrailVisits', 'trail']].dropna(subset=['TrailVisits'])

def get_party_characteristics(siteid):
    return _get_party_characteristics_data(siteid)[['TrailVisits', 'PartyPeople','PartyVehics', 'trail']]