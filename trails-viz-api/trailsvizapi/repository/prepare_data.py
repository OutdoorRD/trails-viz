from pathlib import Path
import os
import pandas as pd
import geopandas as gpd
import trailsvizapi.config.app_config as config

_PROJECT_FILES_ROOT = config.DATA_FILES_ROOT + 'projects/'
_ALLSITES_POLYGONS_FILE = 'allsites.geojson'
_ALLSITES_LINES_FILE = 'allsites_lines.geojson'
_ALLSITES_ACCESS_POINTS_FILE = 'allsites_access_points.geojson'
_ALLSITES_HOME_LOCATIONS_FILE = 'homes_by_site_census.csv'
_MONTHLY_ESTIMATES_FILE = 'viz_model_mmm.csv'
_MONTHLY_ONSITE_FILE = 'viz_model_mmmir.csv'
_WEEKLY_ESTIMATES_FILE = 'viz_model_www.csv'
_WEEKLY_ONSITE_FILE = 'viz_model_wwwir.csv'
_CHATBOT_DATA_FILE = 'chatbot_data.csv'
_STATE_GEOGRAPHIES_DIR = config.DATA_FILES_ROOT + 'geographies/state/'
_COUNTY_GEOGRAPHIES_DIR = config.DATA_FILES_ROOT + 'geographies/county/'
_CENSUS_TRACT_GEOGRAPHIES_DIR = config.DATA_FILES_ROOT + 'geographies/census-tract/'
_CENSUS_ZCTA_GEOGRAPHIES_DIR = config.DATA_FILES_ROOT + 'geographies/zcta/'
_README_DIR = config.DATA_FILES_ROOT + 'readme/'
_SVI_DIR = config.DATA_FILES_ROOT + 'SVI/'
_CHATBOT_DIR = config.DATA_FILES_ROOT + 'chatbot/'

DATA_SOURCE = {}  # A dict is used here for lazy initialization of all the data frames


def _load_geo_df(geo_df_path, geo_df_list):
    '''Load a lines or access points file into a list of all geo dfs'''
    if Path(geo_df_path).exists():
        if geo_df_list is not None:
            geo_df_list = geo_df_list.append(gpd.read_file(geo_df_path), sort=False)
        else:
            geo_df_list = gpd.read_file(geo_df_path)
    return geo_df_list


def _prepare_geo_df(allsites, polygons, new_gdf):
    '''Helper function to merge a new geo df (lines or access points) into the allsites geo df'''
    # only keep required columns
    new_gdf = new_gdf[['siteid', 'geometry']]
    # convert all site ids to string
    new_gdf.loc[:, 'siteid'] = new_gdf['siteid'].astype(str)
    # drop columns if required fields are null
    new_gdf.dropna(inplace=True)
    # trail name and project code is not present in the lines and access point files
    # since, there will be always be a polygon for a site, this info can be extracted
    # from the polygon data frame by doing a merge
    new_gdf = pd.merge(polygons[['siteid', 'Trail_name', 'Prjct_code']],
                       new_gdf, on='siteid', how='right')
    new_gdf.dropna(inplace=True)
    allsites = allsites.append(new_gdf, sort=False)
    return allsites


def _prepare_geo_dfs():
    polygons = None
    lines = None
    access_points = None
    for item in os.listdir(_PROJECT_FILES_ROOT):
        if Path(_PROJECT_FILES_ROOT + item).is_dir():
            polygons_file = _PROJECT_FILES_ROOT + item + '/' + _ALLSITES_POLYGONS_FILE
            polygons = _load_geo_df(polygons_file, polygons)

            lines_file = _PROJECT_FILES_ROOT + item + '/' + _ALLSITES_LINES_FILE
            lines = _load_geo_df(lines_file, lines)

            access_points_file = _PROJECT_FILES_ROOT + item + '/' + _ALLSITES_ACCESS_POINTS_FILE
            access_points = _load_geo_df(access_points_file, access_points)

    # Ensure polygons exists; we may not have access points or lines
    assert polygons is not None

    # only keep required columns
    polygons = polygons[['siteid', 'Trail_name', 'Prjct_code', 'geometry']]

    # convert all site ids to string
    polygons['siteid'] = polygons['siteid'].astype(str)

    # drop columns if required fields are null
    polygons.dropna(subset=['siteid', 'Prjct_code', 'geometry'], inplace=True)

    allsites = polygons.copy()

    # Add in lines and access points (if they exist)
    for geo_df in [lines, access_points]:
        if geo_df is not None:
            allsites = _prepare_geo_df(allsites, polygons, geo_df)
    return allsites


def _prepare_chatbot_data_df():
    chatbot_data_df = None
    if Path(_CHATBOT_DIR + _CHATBOT_DATA_FILE):
        chatbot_data_df = pd.read_csv(_CHATBOT_DIR + _CHATBOT_DATA_FILE, dtype={
            'SiteID': str, 'CountyFIPS': str, 'StateFIPS': str, 'ZipCode': str,
            'from': str, 'to': str, 'InfoSource': str,
        })
    # Convert SiteID from comma-separated string to Python lists
    chatbot_data_df['SiteID'] = chatbot_data_df['SiteID'].apply(
        lambda x: x.split(',') if pd.notna(x) else None
    )
    # Convert InfoSource from comma-separated string to Python lists
    chatbot_data_df['InfoSource'] = chatbot_data_df['InfoSource'].apply(
        lambda x: x.split(',') if pd.notna(x) else None
    )
    assert chatbot_data_df is not None, "Failed to prepare chatbot data."
    return chatbot_data_df


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

    id_cols = ['trail', 'month', 'year'] if period == 'monthly' else ['trail', 'weekstart']

    estimates_df.rename(columns={'jjmm': 'estimate', 'jjmmlg': 'log_estimate'}, inplace=True)
    estimates_onsite.rename(columns={'resp.ss': 'onsite',
                                     'resplg': 'log_onsite',
                                     'resp.ll': 'data_days'}, inplace=True)

    estimates_df.drop(columns='d2p', inplace=True, errors='ignore')
    estimates_onsite.drop(columns='d2p', inplace=True, errors='ignore')

    # convert site id to string, would be helpful later
    estimates_df['trail'] = estimates_df['trail'].astype(str)
    estimates_onsite['trail'] = estimates_onsite['trail'].astype(str)

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
                    df = pd.read_csv(home_locations_file, dtype={'siteid': str, 'tract': str, 'zcta': str})
                    home_locations = home_locations.append(df, sort=False)
                else:
                    home_locations = pd.read_csv(home_locations_file, dtype={'siteid': str, 'tract': str, 'zcta': str})

    # the census tract id is in the format STATEFP COUNTFP TRACTCE. Thus the state code
    # and county code can be extracted by doing a simple substring
    home_locations['state_code'] = home_locations['tract'].str[:2]
    home_locations['county_code'] = home_locations['tract'].str[2:5]

    assert home_locations is not None
    return home_locations


def _prepare_geographies_df(root):
    geographies_list = []
    for item in os.listdir(root):
        file_path = os.path.join(root, item)
        # Check if the file is a .geojson or .shp
        if item.endswith('.geojson') or item.endswith('.shp'):
            gdf = gpd.read_file(file_path)
            geographies_list.append(gdf)
    assert geographies_list
    # Combine all GeoDataFrames
    geographies_df = gpd.GeoDataFrame(pd.concat(geographies_list, ignore_index=True, sort=False))

    return geographies_df


def _prepare_state_boundaries_df():
    state_boundaries_df = _prepare_geographies_df(_STATE_GEOGRAPHIES_DIR)
    state_boundaries_df = state_boundaries_df[['STATEFP', 'NAME', 'geometry']]
    state_boundaries_df.rename(columns={'STATEFP': 'state_code', 'NAME': 'state'}, inplace=True)
    return state_boundaries_df


def _prepare_counties_df():
    counties_df = _prepare_geographies_df(_COUNTY_GEOGRAPHIES_DIR)
    counties_df = counties_df[['STATEFP', 'COUNTYFP', 'NAME', 'geometry']]
    counties_df.rename(columns={'STATEFP': 'state_code', 'COUNTYFP': 'county_code', 'NAME': 'county'}, inplace=True)
    return counties_df


def _prepare_census_tract_df():
    census_tract_df = _prepare_geographies_df(_CENSUS_TRACT_GEOGRAPHIES_DIR)
    census_tract_df = census_tract_df[['zcta', 'fips', 'geometry']]
    return census_tract_df


def _prepare_zcta_df():
    zcta_df = _prepare_geographies_df(_CENSUS_ZCTA_GEOGRAPHIES_DIR)
    return zcta_df


def _prepare_svi_df(geographic_level):
    # extract only required columns
    renamed_columns = {
        'ST': 'state_code',
        'E_TOTPOP': 'population',
        'EP_MINRTY': 'minority_percentage',
        'RPL_THEMES': 'svi'
    }
    if geographic_level == 'TRACT':
        _SVI_DIR_LEVEL = os.path.join(_SVI_DIR, "census-tract/")
        renamed_columns['FIPS'] = 'tract'
    elif geographic_level == 'ZCTA':
        _SVI_DIR_LEVEL = os.path.join(_SVI_DIR, "zcta/")
        renamed_columns['FIPS'] = 'zcta'
    # currently dashboard does not use county level SVI
    # elif geographic_level == 'COUNTY':
    #     _SVI_DIR_LEVEL = os.path.join(_SVI_DIR, "county/")
    #     renamed_columns['FIPS'] = 'county'
    # read the SVI data and merge to it
    svi_df = None
    for item in os.listdir(_SVI_DIR_LEVEL):
        if item.endswith('.csv'):
            file = _SVI_DIR_LEVEL + item
            if svi_df is None:
                svi_df = pd.read_csv(file, dtype={'ST': str, 'FIPS': str})
            else:
                svi_df = svi_df.append(pd.read_csv(file, dtype={'ST': str, 'FIPS': str}), sort=False)
    # Conditionally choose 'EP_PCI' if present, otherwise 'EP_HBURD'
    if 'EP_PCI' in svi_df.columns:
        renamed_columns['EP_PCI'] = 'median_income'
    elif 'EP_HBURD' in svi_df.columns:
        renamed_columns['EP_HBURD'] = 'housing_cost_burden'
    # Select only columns that exist in the DataFrame
    existing_cols = [col for col in renamed_columns.keys() if col in svi_df.columns]
    # Narrow down the DataFrame to these columns
    svi_df = svi_df[existing_cols]
    svi_df.rename(columns=renamed_columns, inplace=True)

    assert svi_df is not None
    return svi_df


def _prepare_project_readme():
    project_readme_cache = dict()

    info_readme_files = [f for f in os.listdir(os.path.join(_README_DIR, 'info')) if f.endswith('.md')]
    visitation_readme_files = [f for f in os.listdir(os.path.join(_README_DIR, 'visitation')) if f.endswith('.md')]
    homelocations_readme_files = [f for f in os.listdir(os.path.join(_README_DIR, 'info')) if f.endswith('.md')]
    
    # read project info file
    for project in config.PROJECT_NAMES.values():
        info_readme_file = list(filter(lambda x: x.split('.')[0] in project, info_readme_files))[0]
        visitation_readme_file = list(filter(lambda x: x.split('.')[0] in project, visitation_readme_files))[0]
        homelocations_readme_file = list(filter(lambda x: x.split('.')[0] in project, homelocations_readme_files))[0]
        with open(os.path.join(_README_DIR, 'info', info_readme_file), 'r', encoding='utf-8') as f:
            project_readme_cache[project] = f.read()
        with open(os.path.join(_README_DIR, 'visitation', visitation_readme_file), 'r', encoding='utf-8') as f:
            project_readme_cache[project + '_VISITS'] = f.read()
        with open(os.path.join(_README_DIR, 'homelocations', homelocations_readme_file), 'r', encoding='utf-8') as f:
            project_readme_cache[project + '_HOMELOCATIONS_INFO'] = f.read()
    return project_readme_cache


def get_from_data_source(key):
    if key not in DATA_SOURCE:
        DATA_SOURCE['ALLSITES_DF'] = _prepare_geo_dfs()
        DATA_SOURCE['MONTHLY_VISITATION_DF'] = _prepare_monthly_df()
        DATA_SOURCE['WEEKLY_VISITATION_DF'] = _prepare_weekly_df()
        DATA_SOURCE['CHATBOT_DATA_DF'] = _prepare_chatbot_data_df()
        DATA_SOURCE['HOME_LOCATIONS_DF'] = _prepare_home_locations_df()
        DATA_SOURCE['STATE_BOUNDARIES_DF'] = _prepare_state_boundaries_df()
        DATA_SOURCE['COUNTIES_DF'] = _prepare_counties_df()
        DATA_SOURCE['CENSUS_TRACT_DF'] = _prepare_census_tract_df()
        DATA_SOURCE['ZCTA_DF'] = _prepare_zcta_df()
        DATA_SOURCE['SVI_TRACT_DF'] = _prepare_svi_df(geographic_level='TRACT')
        # currently dashboard does not use county level SVI
        # DATA_SOURCE['SVI_COUNTY_DF'] = _prepare_svi_df(geographic_level='COUNTY')
        DATA_SOURCE['SVI_ZCTA_DF'] = _prepare_svi_df(geographic_level='ZCTA')
        DATA_SOURCE['PROJECT_README'] = _prepare_project_readme()
    return DATA_SOURCE[key]
