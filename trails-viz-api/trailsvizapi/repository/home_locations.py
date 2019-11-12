from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.sites import get_project_sites


def _treefy_home_locations(id_, home_locations):
    visit_days = home_locations['visit_days'].sum()
    visitors_unq = home_locations['visitors_unq'].sum()
    tree = dict()

    # JSON doesn't recognize any numpy data types, hence must be converted to int
    tree['id'] = id_
    tree['visit_days'] = int(visit_days)
    tree['visitors_unq'] = int(visitors_unq)
    tree['countries'] = []

    for country_idx, country_row in home_locations.groupby(by=['country']).sum().iterrows():
        country_data = {'name': country_idx, 'visit_days': int(country_row['visit_days']),
                        'visitors_unq': int(country_row['visitors_unq']), 'states': []}
        tree['countries'].append(country_data)
        country_df = home_locations[home_locations['country'] == country_idx]

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


def get_home_locations(siteid):
    home_locations = get_from_data_source('HOME_LOCATIONS_DF')
    site_home_locations = home_locations[home_locations['siteid'] == siteid]
    return _treefy_home_locations(siteid, site_home_locations)


def get_project_home_locations(project):
    home_locations = get_from_data_source('HOME_LOCATIONS_DF')
    project_sites = get_project_sites(project)
    project_site_ids = project_sites['siteid'].drop_duplicates()

    project_home_locations = home_locations[home_locations['siteid'].isin(project_site_ids)]

    # International doesn't have state and counties and hence a three column group by will exclude it
    # extra effort to include international
    international_visits = project_home_locations[project_home_locations['country'] == 'International']
    international_visits = international_visits.groupby(['country'], as_index=False).sum()
    project_home_locations = project_home_locations.groupby(by=['country', 'state', 'county'], as_index=False).sum()
    project_home_locations = project_home_locations.append(international_visits, ignore_index=True, sort=False)

    return _treefy_home_locations(project, project_home_locations)


def get_census_tract():
    return get_from_data_source('CENSUS_TRACT')


def get_home_locations_by_census_tract(siteid):
    home_locations = get_from_data_source('HOME_LOCATIONS_CENSUS_TRACT_DF')
    census_tract = get_from_data_source('CENSUS_TRACT')
    site_home_locations = home_locations[home_locations['siteid'] == siteid]
    site_home_census_data = census_tract.merge(site_home_locations, left_on='GEOID', right_on='tract', how='inner')
    return site_home_census_data
