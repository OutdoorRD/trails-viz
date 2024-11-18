import numpy as np
import geopandas as gpd
import pandas as pd
from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.projects_and_sites import get_project_sites

def _get_project_party_characteristics_data(project):
    project_sites = get_project_sites(project)
    siteids = set(project_sites['siteid'].unique())
    party_characteristics_df = get_from_data_source('PARTY_CHARACTERISTICS_DF')
    # Add a 'trail' feature that contains the project site ids (None if observation is not part of project siteids)
    party_characteristics_df['trail'] = party_characteristics_df['SiteID'].apply(lambda lst: next((x for x in lst if x in siteids), None))
    # Return observations with non-missing 'trail' values
    return party_characteristics_df.dropna(subset=['trail'])

def _get_party_characteristics_data(siteid):
    party_characteristics_df = get_from_data_source('PARTY_CHARACTERISTICS_DF')
    party_characteristics_df['trail'] = party_characteristics_df['SiteID'].apply(lambda x: siteid if siteid in x else None)
    return party_characteristics_df.dropna(subset=['trail'])

def get_project_party_characteristics(project):
    return _get_project_party_characteristics_data(project)[['TrailVisits', 'PartyPeople','PartyVehics', 'trail']]

def get_party_characteristics(siteid):
    return _get_party_characteristics_data(siteid)[['TrailVisits', 'PartyPeople','PartyVehics', 'trail']]