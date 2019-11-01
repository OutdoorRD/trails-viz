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


def _prepare_estimates_and_visitation_df(period):
    estimates_file = _MONTHLY_ESTIMATES_FILE if period == 'monthly' else _WEEKLY_ESTIMATES_FILE
    onsite_file = _MONTHLY_ONSITE_FILE if period == 'monthly' else _WEEKLY_ONSITE_FILE

    estimates_df = pd.read_csv(estimates_file)
    estimates_onsite = pd.read_csv(onsite_file)
    estimates_df.rename(columns={'jjmm': 'estimate', 'jjmmlg': 'log_estimate'}, inplace=True)
    estimates_onsite.rename(columns={'resp.ss': 'onsite', 'resplg': 'log_onsite', 'resp.ll': 'data_days'}, inplace=True)

    estimates_df.drop(columns='d2p', inplace=True)
    estimates_onsite.drop(columns='d2p', inplace=True)

    id_cols = ['trail', 'month', 'year']
    return pd.merge(estimates_df, estimates_onsite, on=id_cols, how='outer')


def _prepare_monthly_df():
    return _prepare_estimates_and_visitation_df('monthly')


def _prepare_weekly_df():
    return _prepare_estimates_and_visitation_df('weekly')


def _prepare_home_locations_df():
    home_locations = pd.read_csv(_ALLSITES_HOME_LOCATIONS_FILE)
    return home_locations


def get_from_data_source(key):
    if key not in DATA_SOURCE:
        DATA_SOURCE['ALLSITES_DF'] = _prepare_geo_dfs()
        DATA_SOURCE['MONTHLY_VISITATION_DF'] = _prepare_monthly_df()
        DATA_SOURCE['WEEKLY_VISITATION_DF'] = _prepare_weekly_df()
        DATA_SOURCE['HOME_LOCATIONS_DF'] = _prepare_home_locations_df()

    return DATA_SOURCE[key]
