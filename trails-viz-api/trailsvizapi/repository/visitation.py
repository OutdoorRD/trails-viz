import numpy as np

from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.projects_and_sites import get_project_sites


def get_monthly_visitation(siteid):
    monthly_df = get_from_data_source('MONTHLY_VISITATION_DF')
    site_data = monthly_df[monthly_df['trail'] == siteid]
    return site_data


def get_weekly_visitation(siteid):
    weekly_df = get_from_data_source('WEEKLY_VISITATION_DF')
    site_data = weekly_df[weekly_df['trail'] == siteid]
    return site_data


def _get_project_visitation_data(project, period):
    project_sites = get_project_sites(project)
    project_site_ids = project_sites['siteid'].drop_duplicates()

    if period == 'monthly':
        df = get_from_data_source('MONTHLY_VISITATION_DF')
        group_by_cols = ['year', 'month']
    else:
        df = get_from_data_source('WEEKLY_VISITATION_DF')
        group_by_cols = ['weekstart']

    project_sites_data = df[df['trail'].isin(project_site_ids)]
    project_sites_data = project_sites_data.drop('trail', axis=1)
    project_sites_data = project_sites_data.groupby(group_by_cols, as_index=False).sum()
    project_sites_data['log_estimate'] = np.log(project_sites_data['estimate'] + 1)
    return project_sites_data


def get_project_monthly_visitation(project):
    return _get_project_visitation_data(project, 'monthly')


def get_project_weekly_visitation(project):
    return _get_project_visitation_data(project, 'weekly')


def get_visitation_download_readme(graph):
    visitation_download_readme_cache = get_from_data_source('VISITATION_DOWNLOAD_README')
    return visitation_download_readme_cache[graph]
