import pandas as pd
import geopandas as gpd

import trailsvizapi.app_config as config

_ALLSITES_POLYGONS_FILE = config.DATA_FILES_ROOT + 'allsites.shp'
_ALLSITES_LINES_FILE = config.DATA_FILES_ROOT + 'allsites_lines.geojson'
_ALLSITES_ACCESS_POINTS_FILE = config.DATA_FILES_ROOT + 'allsites_access_points.geojson'
_MONTHLY_ESTIMATES_FILE = config.DATA_FILES_ROOT + 'viz_model_mmm.csv'
_MONTHLY_ONSITE_FILE = config.DATA_FILES_ROOT + 'viz_model_mmmir.csv'
_WEEKLY_ESTIMATES_FILE = config.DATA_FILES_ROOT + 'viz_model_www.csv'
_WEEKLY_ONSITE_FILE = config.DATA_FILES_ROOT + 'viz_model_wwwir.csv'


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


_ALLSITES_DF = _prepare_geo_dfs()
_MONTHLY_VISITATION_DF = _prepare_monthly_df()


def get_project_sites(project_group):
    project_sites = _ALLSITES_DF[_ALLSITES_DF['Prjct_code'].str.contains(project_group)]
    return project_sites


def get_monthly_visitation(siteid):
    site_data = _MONTHLY_VISITATION_DF[_MONTHLY_VISITATION_DF['trail'] == siteid]
    return site_data


def get_monthly_estimates(siteid):
    site_data = _MONTHLY_VISITATION_DF[_MONTHLY_VISITATION_DF['trail'] == siteid]
    mean_site_data = site_data.groupby(by=['month']).mean()
    mean_site_data = mean_site_data[['estimate', 'log_estimate', 'flickr', 'twitter', 'instag', 'wta',
                                     'onsite', 'log_onsite', 'data_days']]
    mean_site_data.reset_index(inplace=True)
    return mean_site_data


def get_annual_estimates(siteid):
    site_data = _MONTHLY_VISITATION_DF[_MONTHLY_VISITATION_DF['trail'] == siteid]
    annual_site_data = site_data.groupby(by=['year']).sum()
    annual_site_data = annual_site_data[['estimate', 'log_estimate', 'flickr', 'twitter', 'instag', 'wta',
                                         'onsite', 'log_onsite', 'data_days']]
    annual_site_data.reset_index(inplace=True)
    return annual_site_data
