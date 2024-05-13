import numpy as np

from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.projects_and_sites import get_project_sites


def _get_estimates(siteid, period):
    monthly_df = get_from_data_source('MONTHLY_VISITATION_DF')
    site_data = monthly_df[monthly_df['trail'] == siteid]
    site_data = site_data.groupby(by=['month']).mean() if period == 'monthly' else site_data.groupby(by=['year']).sum()
    site_data = site_data[['estimate', 'log_estimate', 'flickr', 'twitter',
                           'instag', 'wta', 'alltrails', 'ebird', 'gravy', 
                           'reveal', 'onsite', 'log_onsite', 'data_days']]
    site_data.reset_index(inplace=True)
    return site_data


def get_monthly_estimates(siteid):
    return _get_estimates(siteid, 'monthly')


def get_annual_estimates(siteid):
    return _get_estimates(siteid, 'annual')


def _get_project_estimates(project, period):
    project_sites = get_project_sites(project)
    project_site_ids = project_sites['siteid'].drop_duplicates()
    df = get_from_data_source('MONTHLY_VISITATION_DF')
    project_sites_data = df[df['trail'].isin(project_site_ids)]

    if period == 'monthly':
        project_sites_data = project_sites_data.drop(columns='year').groupby(by=['trail', 'month'],
                                                                             as_index=False).mean()
        project_sites_data = project_sites_data.drop(columns='trail').groupby(by=['month']).sum()
    elif period == 'annual':
        project_sites_data = project_sites_data.drop(columns=['trail', 'month']).groupby(by=['year']).sum()

    project_sites_data = project_sites_data[['estimate', 'log_estimate', 'flickr', 'twitter', 'instag', 'wta',
                                             'alltrails', 'onsite', 'log_onsite', 'data_days']]

    project_sites_data['log_estimate'] = np.log(project_sites_data['estimate'] + 1)
    project_sites_data['log_onsite'] = np.log(project_sites_data['onsite'] + 1)
    project_sites_data.reset_index(drop=False, inplace=True)
    return project_sites_data


def get_project_monthly_estimates(project):
    return _get_project_estimates(project, 'monthly')


def get_project_annual_estimates(project):
    return _get_project_estimates(project, 'annual')


def get_project_last_year_estimates(project):
    project_sites = get_project_sites(project)
    project_site_ids = project_sites['siteid'].drop_duplicates()
    df = get_from_data_source('MONTHLY_VISITATION_DF')
    project_sites_data = df[df['trail'].isin(project_site_ids)]
    project_sites_data = project_sites_data[project_sites_data['year'] == 2018]
    project_sites_data = project_sites_data.groupby(by=['trail'], as_index=False).sum()
    project_sites_data = project_sites_data[['trail', 'estimate']]
    return project_sites_data
