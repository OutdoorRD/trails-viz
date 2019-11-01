from trailsvizapi.repository.prepare_data import get_from_data_source


def get_home_locations(siteid):
    home_locations = get_from_data_source('HOME_LOCATIONS_DF')
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
