from pathlib import Path
import os

import numpy as np
import pandas as pd
import geopandas as gpd

import trailsvizapi.app_config as config

_PROJECT_FILES_ROOT = config.DATA_FILES_ROOT + 'projects/'
_ALLSITES_POLYGONS_FILE = 'allsites.geojson'
_ALLSITES_LINES_FILE = 'allsites_lines.geojson'
_ALLSITES_ACCESS_POINTS_FILE = 'allsites_access_points.geojson'
_ALLSITES_HOME_LOCATIONS_FILE = 'allsites_homes_by_site.csv'
_ALLSITES_HOME_LOCATIONS_CENSUS_TRACT_FILE = 'allsites_homes_by_site_census.csv'
_MONTHLY_ESTIMATES_FILE = 'viz_model_mmm.csv'
_MONTHLY_ONSITE_FILE = 'viz_model_mmmir.csv'
_WEEKLY_ESTIMATES_FILE = 'viz_model_www.csv'
_WEEKLY_ONSITE_FILE = 'viz_model_wwwir.csv'
_CENSUS_TRACT_FILES_DIR = config.DATA_FILES_ROOT + 'census-tract/'
_README_DIR = config.DATA_FILES_ROOT + 'readme/'
_SVI_DIR = config.DATA_FILES_ROOT + 'SVI/'

DATA_SOURCE = {}  # A dict is used here for lazy initialization of all the data frames


def _prepare_geo_dfs():

    polygons = None
    lines = None
    access_points = None
    for item in os.listdir(_PROJECT_FILES_ROOT):
        if Path(_PROJECT_FILES_ROOT + item).is_dir():
            polygons_file = _PROJECT_FILES_ROOT + item + '/' + _ALLSITES_POLYGONS_FILE
            if Path(polygons_file).exists():
                if polygons is not None:
                    polygons = polygons.append(gpd.read_file(polygons_file), sort=False)
                else:
                    polygons = gpd.read_file(polygons_file)

            lines_file = _PROJECT_FILES_ROOT + item + '/' + _ALLSITES_LINES_FILE
            if Path(lines_file).exists():
                if lines is not None:
                    lines = lines.append(gpd.read_file(lines_file), sort=False)
                else:
                    lines = gpd.read_file(lines_file)

            access_points_file = _PROJECT_FILES_ROOT + item + '/' + _ALLSITES_ACCESS_POINTS_FILE
            if Path(access_points_file).exists():
                if access_points is not None:
                    access_points = access_points.append(gpd.read_file(access_points_file), sort=False)
                else:
                    access_points = gpd.read_file(access_points_file)

    assert polygons is not None and lines is not None and access_points is not None

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
    estimates_df = None
    estimates_onsite = None

    estimates_file = _MONTHLY_ESTIMATES_FILE if period == 'monthly' else _WEEKLY_ESTIMATES_FILE
    onsite_file = _MONTHLY_ONSITE_FILE if period == 'monthly' else _WEEKLY_ONSITE_FILE

    for item in os.listdir(_PROJECT_FILES_ROOT):
        if Path(_PROJECT_FILES_ROOT + item).is_dir():
            project_estimates_file = _PROJECT_FILES_ROOT + item + '/' + estimates_file
            if Path(project_estimates_file).exists():
                if estimates_df is not None:
                    estimates_df = estimates_df.append(pd.read_csv(project_estimates_file), sort=False)
                else:
                    estimates_df = pd.read_csv(project_estimates_file)

            project_onsite_file = _PROJECT_FILES_ROOT + item + '/' + onsite_file
            if Path(project_onsite_file).exists():
                if estimates_onsite is not None:
                    estimates_onsite = estimates_onsite.append(pd.read_csv(project_onsite_file), sort=False)
                else:
                    estimates_onsite = pd.read_csv(project_onsite_file)

    assert estimates_df is not None and estimates_onsite is not None

    id_cols = ['trail', 'month', 'year'] if period == 'monthly' else ['trail', 'week', 'month', 'year']

    estimates_df.rename(columns={'jjmm': 'estimate', 'jjmmlg': 'log_estimate'}, inplace=True)
    estimates_onsite.rename(columns={'resp.ss': 'onsite', 'resplg': 'log_onsite', 'resp.ll': 'data_days'}, inplace=True)

    estimates_df.drop(columns='d2p', inplace=True)
    estimates_onsite.drop(columns='d2p', inplace=True)

    return pd.merge(estimates_df, estimates_onsite, on=id_cols, how='outer')


def _prepare_monthly_df():
    return _prepare_estimates_and_visitation_df('monthly')


def _prepare_weekly_df():
    return _prepare_estimates_and_visitation_df('weekly')


def _prepare_home_locations_df():
    home_locations = None
    for item in os.listdir(_PROJECT_FILES_ROOT):
        if Path(_PROJECT_FILES_ROOT + item).is_dir():
            home_locations_file = _PROJECT_FILES_ROOT + item + '/' + _ALLSITES_HOME_LOCATIONS_FILE
            if Path(home_locations_file).exists():
                if home_locations is not None:
                    home_locations = home_locations.append(pd.read_csv(home_locations_file), sort=False)
                else:
                    home_locations = pd.read_csv(home_locations_file)

    assert home_locations is not None
    return home_locations


def _prepare_census_tract_df():
    census_tract_df = None
    for item in os.listdir(_CENSUS_TRACT_FILES_DIR):
        if item.endswith('.geojson'):
            geojson_file = _CENSUS_TRACT_FILES_DIR + item
            if census_tract_df is None:
                census_tract_df = gpd.read_file(geojson_file)
            else:
                census_tract_df = census_tract_df.append(gpd.read_file(geojson_file), sort=False)

    assert census_tract_df is not None

    # keep only required columns
    census_tract_df = census_tract_df[['GEOID', 'geometry']]
    census_tract_df.rename(columns={'GEOID': 'tract'}, inplace=True)
    return census_tract_df


def _prepare_home_locations_census_tract_df():
    data = pd.read_csv(config.DATA_FILES_ROOT + 'allsites_homes_by_site_census.csv')
    data = data.dropna(subset=['tract'])
    data['tract'] = data['tract'].astype(np.int64)
    data['tract'] = data['tract'].astype(str)

    # read the SVI data and merge to it
    svi_df = None
    for item in os.listdir(_SVI_DIR):
        if item.endswith('.csv'):
            file = _SVI_DIR + item
            if svi_df is None:
                svi_df = pd.read_csv(file)
            else:
                svi_df = svi_df.append(pd.read_csv(file), sort=False)

    # extract only required columns
    renamed_columns = {
        'FIPS': 'tract',
        'E_TOTPOP': 'population',
        'EP_PCI': 'median_income',
        'EP_MINRTY': 'minority_percentage',
        'RPL_THEMES': 'svi'
    }
    svi_df = svi_df[list(renamed_columns.keys())]
    svi_df.rename(columns=renamed_columns, inplace=True)
    svi_df['tract'] = svi_df['tract'].astype(str)

    assert svi_df is not None

    data = data.merge(svi_df, how='left', on='tract')

    return data


def _prepare_project_readme():
    project_readme_cache = dict()
    readme_files = os.listdir(_README_DIR)
    readme_files = list(filter(lambda x: x.endswith('.md'), readme_files))
    for project in config.PROJECT_NAMES.values():
        project_readme_file = list(filter(lambda x: x.split('.')[0] in project, readme_files))[0]
        with open(_README_DIR + project_readme_file, 'r', encoding='utf-8') as f:
            project_readme_cache[project] = f.read()

    # read the visitation info file
    visit_readme_files = list(filter(lambda x: x.endswith('_visits.md'), readme_files))
    for project in config.PROJECT_NAMES.values():
        visit_readme = list(filter(lambda x: x.split('_')[0].upper() in project, readme_files))[0]
        with open(_README_DIR + visit_readme, 'r', encoding='utf-8') as f:
            project_readme_cache[project + '_VISITS'] = f.read()

    # read the generic home locations info readme
    with open(_README_DIR + 'homelocations_info.md', 'r', encoding='utf-8') as f:
        project_readme_cache['HOMELOCATIONS_INFO'] = f.read()

    return project_readme_cache


def get_from_data_source(key):
    if key not in DATA_SOURCE:
        DATA_SOURCE['ALLSITES_DF'] = _prepare_geo_dfs()
        DATA_SOURCE['MONTHLY_VISITATION_DF'] = _prepare_monthly_df()
        DATA_SOURCE['WEEKLY_VISITATION_DF'] = _prepare_weekly_df()
        DATA_SOURCE['HOME_LOCATIONS_DF'] = _prepare_home_locations_df()
        DATA_SOURCE['CENSUS_TRACT'] = _prepare_census_tract_df()
        DATA_SOURCE['HOME_LOCATIONS_CENSUS_TRACT_DF'] = _prepare_home_locations_census_tract_df()
        DATA_SOURCE['PROJECT_README'] = _prepare_project_readme()

    return DATA_SOURCE[key]
