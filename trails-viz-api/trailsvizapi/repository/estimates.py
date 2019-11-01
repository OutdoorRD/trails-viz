from trailsvizapi.repository.prepare_data import get_from_data_source


def _get_estimates(siteid, period):
    monthly_df = get_from_data_source('MONTHLY_VISITATION_DF')
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