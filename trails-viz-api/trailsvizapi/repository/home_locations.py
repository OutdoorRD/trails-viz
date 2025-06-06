from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.projects_and_sites import get_project_sites


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


def get_project_home_locations_df(project, source, year_start=None, year_end=None):
    project_sites = get_project_sites(project)
    project_site_ids = set(project_sites['siteid'].drop_duplicates())
    if source == 'chatbot':
        chatbot_data_df = get_from_data_source('CHATBOT_DATA_DF').copy()
        # Add a 'trail' feature that contains the project assoicated site id.
        # 'trail' value set to None if no site ids in 'SiteID' are not included in the list of project siteids.
        chatbot_data_df['trail'] = chatbot_data_df['SiteID'].apply(
            lambda lst: next((x for x in lst if x in project_site_ids), None))
        # keep observations with non-missing 'trail' values
        chatbot_data_df = chatbot_data_df.dropna(subset=['trail'])

        # If a 'date' column exists, convert it to datetime and filter by year_start and year_end if provided.
        if 'year' in chatbot_data_df.columns:
            if year_start is not None:
                chatbot_data_df = chatbot_data_df[chatbot_data_df['year'] >= int(year_start)]
            if year_end is not None:
                chatbot_data_df = chatbot_data_df[chatbot_data_df['year'] <= int(year_end)]

        project_home_locations = get_chatbot_home_locations_df(chatbot_data_df)
    else:
        home_locations = get_from_data_source('HOME_LOCATIONS_DF')
        project_home_locations = home_locations[home_locations['siteid'].isin(project_site_ids)]
    return project_home_locations


def get_site_home_locations_df(siteid, source, year_start=None, year_end=None):

    if source == 'chatbot':
        chatbot_data_df = get_from_data_source('CHATBOT_DATA_DF')
        chatbot_site_data_df = chatbot_data_df[chatbot_data_df['SiteID'].apply(lambda x: siteid in x if x else False)]
        # If a 'date' column exists, convert to datetime and filter by year range
        if 'year' in chatbot_site_data_df.columns:
            if year_start is not None:
                chatbot_site_data_df = chatbot_site_data_df[chatbot_site_data_df['year'] >= int(year_start)]
            if year_end is not None:
                chatbot_site_data_df = chatbot_site_data_df[chatbot_site_data_df['year'] <= int(year_end)]
        site_home_locations = get_chatbot_home_locations_df(chatbot_site_data_df)
    else:
        home_locations = get_from_data_source('HOME_LOCATIONS_DF')
        site_home_locations = home_locations[home_locations['siteid'] == siteid]
    return site_home_locations


def get_chatbot_home_locations_df(df):
    home_locations = df.groupby(['County', 'State', 'Country', 'CountyFIPS', 'StateFIPS', 'ZipCode']).agg(
        visit_days=('from', 'count'),
        visitors_unq=('from', 'nunique'),
        age_sum=('Age', 'sum'),
        age_count=('Age', 'count')
    ).reset_index()
    home_locations = home_locations.rename(columns={
        'County': 'county',
        'CountyFIPS': 'county_code',
        'StateFIPS': 'state_code',
        'State': 'state',
        'Country': 'country',
        'ZipCode': 'zcta'
    })
    return home_locations


def get_home_locations(siteid, source, year_start=None, year_end=None):
    site_home_locations = get_site_home_locations_df(siteid, source, year_start, year_end)
    return _treefy_home_locations(siteid, site_home_locations)


def get_project_home_locations(project, source, year_start=None, year_end=None):
    project_home_locations = get_project_home_locations_df(project, source, year_start, year_end)
    # International doesn't have state and counties and hence a three column group by will exclude it
    # extra effort to include international
    international_visits = project_home_locations[project_home_locations['country'] == 'International']
    international_visits = international_visits.groupby(['country'], as_index=False).sum()
    project_home_locations = project_home_locations.groupby(by=['country', 'state', 'county'], as_index=False).sum()
    project_home_locations = project_home_locations.append(international_visits, ignore_index=True, sort=False)
    return _treefy_home_locations(project, project_home_locations)


def get_home_locations_by_state(siteid, source, year_start=None, year_end=None):
    site_home_locations = get_site_home_locations_df(siteid, source, year_start, year_end)
    state_boundaries = get_from_data_source('STATE_BOUNDARIES_DF')
    site_home_locations = site_home_locations[['state_code', 'state', 'visit_days', 'visitors_unq']]
    site_home_locations = site_home_locations.groupby(by=['state_code', 'state'], as_index=False).sum()
    site_home_state_data = state_boundaries.merge(site_home_locations, on=['state_code', 'state'], how='inner')
    return site_home_state_data


def get_project_home_locations_by_state(project, source, year_start=None, year_end=None):
    state_boundaries = get_from_data_source('STATE_BOUNDARIES_DF')
    project_home_locations = get_project_home_locations_df(project, source, year_start, year_end)
    project_home_locations = project_home_locations[['state_code', 'state', 'visit_days', 'visitors_unq']]
    project_home_locations = project_home_locations.groupby(by=['state_code', 'state'], as_index=False).sum()
    project_home_state_data = state_boundaries.merge(project_home_locations, on=['state_code', 'state'], how='inner')
    return project_home_state_data


def get_home_locations_by_county(siteid, source, state_code, year_start=None, year_end=None):
    site_home_locations = get_site_home_locations_df(siteid, source, year_start, year_end)
    site_home_locations = site_home_locations[site_home_locations['state_code'] == state_code]
    county_geographies = get_from_data_source('COUNTIES_DF')
    county_geographies = county_geographies[county_geographies['state_code'] == state_code]
    site_home_locations = site_home_locations[['county_code', 'county', 'visit_days', 'visitors_unq']]
    site_home_locations = site_home_locations.groupby(by=['county_code', 'county'], as_index=False).sum()
    site_home_county_data = county_geographies.merge(site_home_locations, on=['county_code', 'county'], how='inner')
    return site_home_county_data


def get_project_home_locations_by_county(project, source, state_code, year_start=None, year_end=None):
    county_geographies = get_from_data_source('COUNTIES_DF')
    county_geographies = county_geographies[county_geographies['state_code'] == state_code]
    project_home_locations = get_project_home_locations_df(project, source, year_start, year_end)
    project_home_locations = project_home_locations[project_home_locations['state_code'] == state_code]
    project_home_locations = project_home_locations[['county_code', 'county', 'visit_days', 'visitors_unq']]
    project_home_locations = project_home_locations.groupby(by=['county_code', 'county'], as_index=False).sum()
    project_home_county_data = county_geographies.merge(project_home_locations,
                                                        on=['county_code', 'county'], how='inner')
    return project_home_county_data


def get_home_locations_by_census_tract(siteid, source, state_code, county_code, zcta_code):
    if source == 'chatbot':
        return None
    census_tract_geographies = get_from_data_source('CENSUS_TRACT_DF')
    census_tract_geographies = census_tract_geographies[
        (census_tract_geographies['fips'].str[:5] == (str(state_code) + str(county_code)))
        & (census_tract_geographies['zcta'] == zcta_code)
    ]

    home_locations = get_from_data_source('HOME_LOCATIONS_DF')
    site_home_locations = home_locations[(home_locations['siteid'] == siteid)
                                         & (home_locations['state_code'] == state_code)
                                         & (home_locations['county_code'] == county_code)]

    site_home_locations = site_home_locations[['tract', 'visit_days', 'visitors_unq']]
    site_home_census_data = census_tract_geographies.merge(site_home_locations, left_on='fips',
                                                           right_on='tract', how='inner')

    svi_df = get_from_data_source('SVI_TRACT_DF')
    svi_df = svi_df[svi_df['state_code'] == state_code]
    svi_df = svi_df.drop(columns=['state_code'])
    site_home_census_data = site_home_census_data.merge(svi_df, on='tract', how='inner')

    return site_home_census_data


def get_home_locations_by_zcta(siteid, source, state_code, county_code, year_start=None, year_end=None):
    zcta_geographies = get_from_data_source('ZCTA_DF')
    st_county = str(state_code) + str(county_code)
    zcta_geographies = zcta_geographies[zcta_geographies['st_county'] == st_county]
    site_home_locations = get_site_home_locations_df(siteid, source, year_start, year_end)
    site_home_locations = site_home_locations[(site_home_locations['state_code'] == state_code)
                                              & (site_home_locations['county_code'] == county_code)]

    if 'zcta' not in site_home_locations.columns:
        return None
    agg_dict = {
        'visit_days': ('visit_days', 'sum'),
        'visitors_unq': ('visitors_unq', 'sum'),
    }
    if {'age_sum', 'age_count'}.issubset(site_home_locations.columns):
        agg_dict.update({
            'age_sum': ('age_sum', 'sum'),
            'age_count': ('age_count', 'sum')
        })

    site_home_locations = site_home_locations.groupby(
        ['state_code', 'county_code', 'zcta']
    ).agg(**agg_dict).reset_index()

    if {'age_sum', 'age_count'}.issubset(site_home_locations.columns):
        site_home_locations['reported_mean_age'] = (
            site_home_locations['age_sum'] / site_home_locations['age_count']
        )

    site_home_census_data = zcta_geographies.merge(site_home_locations, on='zcta', how='inner')

    svi_df = get_from_data_source('SVI_ZCTA_DF')
    site_home_census_data = site_home_census_data.merge(svi_df, on='zcta', how='inner')
    return site_home_census_data


def get_project_home_locations_by_census_tract(project, source, state_code, county_code, zcta_code):
    if source == 'chatbot':
        return None
    census_tract_geographies = get_from_data_source('CENSUS_TRACT_DF')
    census_tract_geographies = census_tract_geographies[
        (census_tract_geographies['fips'].str[:5] == (str(state_code) + str(county_code)))
        & (census_tract_geographies['zcta'] == zcta_code)
    ]

    project_sites = get_project_sites(project)
    project_site_ids = project_sites['siteid'].drop_duplicates()

    home_locations = get_from_data_source('HOME_LOCATIONS_DF')
    project_home_locations = home_locations[(home_locations['siteid'].isin(project_site_ids))
                                            & (home_locations['state_code'] == state_code)
                                            & (home_locations['county_code'] == county_code)]

    # for each tract, we need to sum visit days and visitors_unq
    project_home_locations = project_home_locations.groupby(by=['tract'],
                                                            as_index=False)['visit_days', 'visitors_unq'].sum()

    # project_home_census_data = census_tract_geographies.merge(project_home_locations, on='tract', how='inner')
    project_home_census_data = census_tract_geographies.merge(project_home_locations, left_on='fips',
                                                              right_on='tract', how='inner')

    svi_df = get_from_data_source('SVI_TRACT_DF')
    svi_df = svi_df[svi_df['state_code'] == state_code]
    svi_df = svi_df.drop(columns=['state_code'])
    project_home_census_data = project_home_census_data.merge(svi_df, on='tract', how='inner')

    return project_home_census_data


def get_project_home_locations_by_zcta(project, source, state_code, county_code, year_start=None, year_end=None):
    zcta_geographies = get_from_data_source('ZCTA_DF')
    st_county = str(state_code) + str(county_code)
    zcta_geographies = zcta_geographies[zcta_geographies['st_county'] == st_county]
    project_home_locations = get_project_home_locations_df(project, source, year_start, year_end)
    project_home_locations = project_home_locations[(project_home_locations['state_code'] == state_code)
                                                    & (project_home_locations['county_code'] == county_code)]
    if 'zcta' not in project_home_locations.columns:
        return None

    agg_dict = {
        'visit_days': ('visit_days', 'sum'),
        'visitors_unq': ('visitors_unq', 'sum'),
    }
    if {'age_sum', 'age_count'}.issubset(project_home_locations.columns):
        agg_dict.update({
            'age_sum': ('age_sum', 'sum'),
            'age_count': ('age_count', 'sum')
        })

    project_home_locations = project_home_locations.groupby(
                                                            ['state_code', 'county_code', 'zcta']
                                                            ).agg(**agg_dict).reset_index()
    if {'age_sum', 'age_count'}.issubset(project_home_locations.columns):
        project_home_locations['reported_mean_age'] = (
            project_home_locations['age_sum'] / project_home_locations['age_count']
        )
    project_home_census_data = zcta_geographies.merge(project_home_locations, on='zcta', how='inner')
    svi_df = get_from_data_source('SVI_ZCTA_DF')
    project_home_census_data = project_home_census_data.merge(svi_df, on='zcta', how='inner')
    return project_home_census_data


def get_demographic_summary(siteid, source, year_start=None, year_end=None):
    site_home_locations = get_site_home_locations_df(siteid, source, year_start, year_end)
    if 'zcta' not in site_home_locations.columns:
        return None
    site_home_locations = site_home_locations.groupby(by=['zcta'], as_index=False).sum()
    svi_df = get_from_data_source('SVI_ZCTA_DF')
    demographics_data = site_home_locations.merge(svi_df, on='zcta', how='inner')
    return demographics_data


def get_project_demographic_summary(project, source, year_start=None, year_end=None):
    project_home_locations = get_project_home_locations_df(project, source, year_start, year_end)
    if source == 'chatbot':
        project_home_locations = project_home_locations.groupby(by=['zcta'], as_index=False).sum()
        svi_df = get_from_data_source('SVI_ZCTA_DF')
        demographics_data = project_home_locations.merge(svi_df, on='zcta', how='inner')
    else:
        project_home_locations = project_home_locations.groupby(by=['tract'], as_index=False).sum()
        svi_df = get_from_data_source('SVI_TRACT_DF')
        demographics_data = project_home_locations.merge(svi_df, on='tract', how='inner')
    return demographics_data
