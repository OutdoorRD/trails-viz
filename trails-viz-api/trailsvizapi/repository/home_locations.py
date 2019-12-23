from trailsvizapi.config import app_config
from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.projects_and_sites import get_project_sites, get_project_from_site


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


def get_home_locations_by_state(siteid):
    state_boundaries = get_from_data_source('STATE_BOUNDARIES_DF')
    home_locations = get_from_data_source('HOME_LOCATIONS_DF')
    site_home_locations = home_locations[home_locations['siteid'] == siteid]
    site_home_locations = site_home_locations[['state_code', 'state', 'visit_days', 'visitors_unq']]
    site_home_locations = site_home_locations.groupby(by=['state_code', 'state'], as_index=False).sum()
    site_home_state_data = state_boundaries.merge(site_home_locations, on=['state_code', 'state'], how='inner')
    return site_home_state_data


def get_project_home_locations_by_state(project):
    state_boundaries = get_from_data_source('STATE_BOUNDARIES_DF')
    home_locations = get_from_data_source('HOME_LOCATIONS_DF')

    project_sites = get_project_sites(project)
    project_site_ids = project_sites['siteid'].drop_duplicates()

    project_home_locations = home_locations[home_locations['siteid'].isin(project_site_ids)]
    project_home_locations = project_home_locations[['state_code', 'state', 'visit_days', 'visitors_unq']]

    project_home_locations = project_home_locations.groupby(by=['state_code', 'state'], as_index=False).sum()
    project_home_state_data = state_boundaries.merge(project_home_locations, on=['state_code', 'state'], how='inner')
    return project_home_state_data


def get_home_locations_by_county(siteid, state_code):
    county_geographies = get_from_data_source('COUNTIES_DF')
    county_geographies = county_geographies[county_geographies['state_code'] == state_code]

    home_locations = get_from_data_source('HOME_LOCATIONS_DF')
    site_home_locations = home_locations[(home_locations['siteid'] == siteid)
                                         & (home_locations['state_code'] == state_code)]

    site_home_locations = site_home_locations[['county_code', 'county', 'visit_days', 'visitors_unq']]
    site_home_locations = site_home_locations.groupby(by=['county_code', 'county'], as_index=False).sum()

    site_home_county_data = county_geographies.merge(site_home_locations, on=['county_code', 'county'], how='inner')
    return site_home_county_data


def get_project_home_locations_by_county(project, state_code):
    county_geographies = get_from_data_source('COUNTIES_DF')
    county_geographies = county_geographies[county_geographies['state_code'] == state_code]

    home_locations = get_from_data_source('HOME_LOCATIONS_DF')

    project_sites = get_project_sites(project)
    project_site_ids = project_sites['siteid'].drop_duplicates()

    project_home_locations = home_locations[(home_locations['siteid'].isin(project_site_ids))
                                            & (home_locations['state_code'] == state_code)]

    project_home_locations = project_home_locations[['county_code', 'county', 'visit_days', 'visitors_unq']]
    project_home_locations = project_home_locations.groupby(by=['county_code', 'county'], as_index=False).sum()

    project_home_county_data = county_geographies.merge(project_home_locations,
                                                        on=['county_code', 'county'], how='inner')
    return project_home_county_data


def get_home_locations_by_census_tract(siteid, state_code, county_code):
    census_tract_geographies = get_from_data_source('CENSUS_TRACT_DF')
    census_tract_geographies = census_tract_geographies[(census_tract_geographies['state_code'] == state_code)
                                                        & (census_tract_geographies['county_code'] == county_code)]

    home_locations = get_from_data_source('HOME_LOCATIONS_DF')
    site_home_locations = home_locations[(home_locations['siteid'] == siteid)
                                         & (home_locations['state_code'] == state_code)
                                         & (home_locations['county_code'] == county_code)]

    site_home_locations = site_home_locations[['tract', 'visit_days', 'visitors_unq']]
    site_home_census_data = census_tract_geographies.merge(site_home_locations, on='tract', how='inner')

    svi_df = get_from_data_source('SVI_DF')
    svi_df = svi_df[svi_df['state_code'] == state_code]
    svi_df = svi_df.drop(columns=['state_code'])
    site_home_census_data = site_home_census_data.merge(svi_df, on='tract', how='inner')

    return site_home_census_data


def get_project_home_locations_by_census_tract(project, state_code, county_code):
    census_tract_geographies = get_from_data_source('CENSUS_TRACT_DF')
    census_tract_geographies = census_tract_geographies[(census_tract_geographies['state_code'] == state_code)
                                                        & (census_tract_geographies['county_code'] == county_code)]

    project_sites = get_project_sites(project)
    project_site_ids = project_sites['siteid'].drop_duplicates()

    home_locations = get_from_data_source('HOME_LOCATIONS_DF')
    project_home_locations = home_locations[(home_locations['siteid'].isin(project_site_ids))
                                            & (home_locations['state_code'] == state_code)
                                            & (home_locations['county_code'] == county_code)]

    # for each tract, we need to sum visit days and visitors_unq
    project_home_locations = project_home_locations.groupby(by=['tract'],
                                                            as_index=False)['visit_days', 'visitors_unq'].sum()
    project_home_census_data = census_tract_geographies.merge(project_home_locations, on='tract', how='inner')

    svi_df = get_from_data_source('SVI_DF')
    svi_df = svi_df[svi_df['state_code'] == state_code]
    svi_df = svi_df.drop(columns=['state_code'])
    project_home_census_data = project_home_census_data.merge(svi_df, on='tract', how='inner')

    return project_home_census_data


def get_demographic_summary(siteid):
    svi_df = get_from_data_source('SVI_DF')
    home_locations = get_from_data_source('HOME_LOCATIONS_DF')

    project = get_project_from_site(siteid)
    census_tract_states = app_config.CENSUS_TRACT_STATES[project]
    svi_df = svi_df[svi_df['state_code'].isin(census_tract_states)]
    svi_df = svi_df.drop(columns=['state_code'])

    site_home_locations = home_locations[home_locations['siteid'] == siteid]
    demographics_data = site_home_locations.merge(svi_df, on='tract', how='inner')
    return demographics_data


def get_project_demographic_summary(project):
    svi_df = get_from_data_source('SVI_DF')
    home_locations = get_from_data_source('HOME_LOCATIONS_DF')

    project_sites = get_project_sites(project)
    project_site_ids = project_sites['siteid'].drop_duplicates()

    project_home_locations = home_locations[home_locations['siteid'].isin(project_site_ids)]
    project_home_locations = project_home_locations.groupby(by=['tract'], as_index=False).sum()

    census_tract_states = app_config.CENSUS_TRACT_STATES[project]
    svi_df = svi_df[svi_df['state_code'].isin(census_tract_states)]
    svi_df = svi_df.drop(columns=['state_code'])
    demographics_data = project_home_locations.merge(svi_df, on='tract', how='inner')
    return demographics_data
