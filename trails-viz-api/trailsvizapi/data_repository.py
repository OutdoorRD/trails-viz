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

    # trail name and project code is not present in the lines and access point files
    # since, there will be always be a polygon for a site, this info can be extracted
    # from the polygon data frame by doing a merge
    poly_line_merge = pd.merge(polygons[['siteid', 'Trail_name', 'Prjct_code']],
                               lines['siteid'], on='siteid', how='left')
    poly_access_merge = pd.merge(polygons[['siteid', 'Trail_name', 'Prjct_code']],
                                 access_points['siteid'], on='siteid', how='left')

    lines[['Trail_name', 'Prjct_code']] = poly_line_merge[['Trail_name', 'Prjct_code']]
    access_points[['Trail_name', 'Prjct_code']] = poly_access_merge[['Trail_name', 'Prjct_code']]

    return polygons.append(lines, sort=False).append(access_points, sort=False)


_ALLSITES_DF = _prepare_geo_dfs()


def get_project_sites(project_group):
    project_sites = _ALLSITES_DF[_ALLSITES_DF['Prjct_code'].str.contains(project_group)]
    return project_sites
