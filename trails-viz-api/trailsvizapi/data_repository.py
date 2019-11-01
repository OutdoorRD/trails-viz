import numpy as np
import pandas as pd
import geopandas as gpd

import trailsvizapi.app_config as config

_ALLSITES_POLYGONS_FILE = config.DATA_FILES_ROOT + 'allsites.shp'
_ALLSITES_LINES_FILE = config.DATA_FILES_ROOT + 'allsites_lines.geojson'
_ALLSITES_ACCESS_POINTS_FILE = config.DATA_FILES_ROOT + 'allsites_access_points.geojson'
_ALLSITES_HOME_LOCATIONS_FILE = config.DATA_FILES_ROOT + 'allsites_homes_by_site.csv'
_MONTHLY_ESTIMATES_FILE = config.DATA_FILES_ROOT + 'viz_model_mmm.csv'
_MONTHLY_ONSITE_FILE = config.DATA_FILES_ROOT + 'viz_model_mmmir.csv'
_WEEKLY_ESTIMATES_FILE = config.DATA_FILES_ROOT + 'viz_model_www.csv'
_WEEKLY_ONSITE_FILE = config.DATA_FILES_ROOT + 'viz_model_wwwir.csv'

DATA_SOURCE = {}  # A dict is used here for lazy initialization of all the data frames


def _prepare_geo_dfs():
    polygons = gpd.read_file(_ALLSITES_POLYGONS_FILE)
    lines = gpd.read_file(_ALLSITES_LINES_FILE)
    access_points = gpd.read_file(_ALLSITES_ACCESS_POINTS_FILE)

    # only keep required columns
    polygons = polygons[['siteid', 'Trail_name', 'Prjct_code', 'geometry']]
    lines = lines[['siteid', 'geometry']]
    access_points = access_points[['siteid', 'geometry']]

    # convert siteid from lines and access points to numeric
    lines['siteid'] = pd.to_numeric(lines['siteid'])
    access_points['siteid'] = pd.to_numeric(access_points['siteid'])

    # drop columns if required fields are null
    polygons.dropna(subset=['siteid', 'Prjct_code', 'geometry'], inplace=True)
    lines.dropna(inplace=True)
    access_points.dropna(inplace=True)

    # trail name and project code is not present in the lines and access point files
    # since, there will be always be a polygon for a site, this info can be extracted
    # from the polygon data frame by doing a merge
    lines = pd.merge(polygons[['siteid', 'Trail_name', 'Prjct_code']],
                     lines, on='siteid', how='right')
    access_points = pd.merge(polygons[['siteid', 'Trail_name', 'Prjct_code']],
                             access_points, on='siteid', how='right')

    lines.dropna(inplace=True)
    access_points.dropna(inplace=True)

    allsites = polygons.append(lines, sort=False).append(access_points, sort=False)
    return allsites


def _prepare_monthly_df():
    monthly_estimate = pd.read_csv(_MONTHLY_ESTIMATES_FILE)
    monthly_onsite = pd.read_csv(_MONTHLY_ONSITE_FILE)
    monthly_estimate.rename(columns={'jjmm': 'estimate', 'jjmmlg': 'log_estimate'}, inplace=True)
    monthly_onsite.rename(columns={'resp.ss': 'onsite', 'resplg': 'log_onsite', 'resp.ll': 'data_days'}, inplace=True)

    monthly_estimate.drop(columns='d2p', inplace=True)
    monthly_onsite.drop(columns='d2p', inplace=True)

    id_cols = ['trail', 'month', 'year']
    return pd.merge(monthly_estimate, monthly_onsite, on=id_cols, how='outer')


def _prepare_weekly_df():
    weekly_estimate = pd.read_csv(_WEEKLY_ESTIMATES_FILE)
    weekly_onsite = pd.read_csv(_WEEKLY_ONSITE_FILE)

    weekly_estimate.rename(columns={'jjmm': 'estimate', 'jjmmlg': 'log_estimate'}, inplace=True)
    weekly_onsite.rename(columns={'resp.ss': 'onsite', 'resplg': 'log_onsite', 'resp.ll': 'data_days'}, inplace=True)

    weekly_estimate.drop(columns='d2p', inplace=True)
    weekly_onsite.drop(columns='d2p', inplace=True)

    id_cols = ['trail', 'week', 'month', 'year']
    return pd.merge(weekly_estimate, weekly_onsite, on=id_cols, how='outer')


def _prepare_home_locations_df():
    home_locations = pd.read_csv(_ALLSITES_HOME_LOCATIONS_FILE)
    return home_locations


def _get_from_data_source(key):
    if key not in DATA_SOURCE:
        DATA_SOURCE['ALLSITES_DF'] = _prepare_geo_dfs()
        DATA_SOURCE['MONTHLY_VISITATION_DF'] = _prepare_monthly_df()
        DATA_SOURCE['WEEKLY_VISITATION_DF'] = _prepare_weekly_df()
        DATA_SOURCE['HOME_LOCATIONS_DF'] = _prepare_home_locations_df()

    return DATA_SOURCE[key]


def get_project_sites(project_group):
    allsites = _get_from_data_source('ALLSITES_DF')
    project_sites = allsites[allsites['Prjct_code'].str.contains(project_group)]
    return project_sites


def _get_project_visitation_data(project, period):
    project_sites = get_project_sites(project)
    project_site_ids = project_sites['siteid'].drop_duplicates()

    if period == 'monthly':
        df = _get_from_data_source('MONTHLY_VISITATION_DF')
        group_by_cols = ['year', 'month']
    else:
        df = _get_from_data_source('WEEKLY_VISITATION_DF')
        group_by_cols = ['year', 'month', 'week']

    project_sites_data = df[df['trail'].isin(project_site_ids)]
    project_sites_data = project_sites_data.drop('trail', axis=1)
    project_sites_data = project_sites_data.groupby(group_by_cols, as_index=False).sum()
    project_sites_data['log_estimate'] = np.log(project_sites_data['estimate'] + 1)
    return project_sites_data


def get_project_monthly_visitation(project):
    return _get_project_visitation_data(project, 'monthly')


def get_project_weekly_visitation(project):
    return _get_project_visitation_data(project, 'weekly')


def get_monthly_visitation(siteid):
    monthly_df = _get_from_data_source('MONTHLY_VISITATION_DF')
    site_data = monthly_df[monthly_df['trail'] == siteid]
    return site_data


def get_weekly_visitation(siteid):
    weekly_df = _get_from_data_source('WEEKLY_VISITATION_DF')
    site_data = weekly_df[weekly_df['trail'] == siteid]
    return site_data


def _get_estimates(siteid, period):
    monthly_df = _get_from_data_source('MONTHLY_VISITATION_DF')
    site_data = monthly_df[monthly_df['trail'] == siteid]
    if period == 'monthly':
        site_data = site_data.groupby(by=['month']).mean()
    elif period == 'annual':
        site_data = site_data.groupby(by=['year']).sum()

    site_data = site_data[['estimate', 'log_estimate', 'flickr', 'twitter', 'instag', 'wta',
                           'onsite', 'log_onsite', 'data_days']]
    site_data.reset_index(inplace=True)
    return site_data


def get_monthly_estimates(siteid):
    return _get_estimates(siteid, 'monthly')


def get_annual_estimates(siteid):
    return _get_estimates(siteid, 'annual')


def get_home_locations(siteid):
    home_locations = _get_from_data_source('HOME_LOCATIONS_DF')
    site_home_locations = home_locations[home_locations['siteid'] == siteid]
    visit_days = site_home_locations['visit_days'].sum()
    visitors_unq = site_home_locations['visitors_unq'].sum()
    tree = dict()

    # JSON doesn't recognize any numpy data types, hence must be converted to int
    tree['siteid'] = int(site_home_locations.iloc[0, 0])
    tree['visit_days'] = int(visit_days)
    tree['visitors_unq'] = int(visitors_unq)
    tree['countries'] = []

    for country_idx, country_row in site_home_locations.groupby(by=['country']).sum().iterrows():
        country_data = {'name': country_idx, 'visit_days': int(country_row['visit_days']),
                        'visitors_unq': int(country_row['visitors_unq']),  'states': []}
        tree['countries'].append(country_data)
        country_df = site_home_locations[site_home_locations['country'] == country_idx]

        for state_idx, state_row in country_df.groupby(by=['state']).sum().iterrows():
            state_data = {'name': state_idx, 'visit_days': int(state_row['visit_days']),
                          'visitors_unq': int(state_row['visitors_unq']), 'counties': []}
            country_data['states'].append(state_data)
            state_df = country_df[country_df['state'] == state_idx]

            for county_idx, county_row in state_df.groupby(by=['county']).sum().iterrows():
                county_data = {'name': county_idx, 'visit_days': int(county_row['visit_days']),
                               'visitors_unq': int(county_row['visitors_unq'])}
                state_data['counties'].append(county_data)

    return tree
