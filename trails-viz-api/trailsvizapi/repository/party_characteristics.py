from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.projects_and_sites import get_project_sites
import pandas as pd
import numpy as np
import math

CONFIDENCE_LEVEL = 1.96
PARTY_CHARACTERISTICS = ['TrailVisits', 'PartyPeople', 'PartyVehics', 'PeoplePerVehics']


def get_project_party_characteristics(project):
    project_sites = get_project_sites(project)
    siteids = set(project_sites['siteid'].unique())
    party_characteristics_df = _prepare_party_characteristics_wide_format(siteids=siteids)
    if party_characteristics_df.empty:
        return party_characteristics_df
    return _convert_wide_to_long_format(party_characteristics_df).dropna(subset=['value'])


def get_party_characteristics(siteid):
    party_characteristics_df = _prepare_party_characteristics_wide_format(siteid=siteid)
    if party_characteristics_df.empty:
        return party_characteristics_df
    return _convert_wide_to_long_format(party_characteristics_df).dropna(subset=['value'])


def get_project_party_characteristics_yearly_statistics(project):
    project_sites = get_project_sites(project)
    siteids = set(project_sites['siteid'].unique())
    party_characteristics_df = _prepare_party_characteristics_wide_format(siteids=siteids)
    if party_characteristics_df.empty:
        return _generate_empty_time_series_response()
    party_characteristics_df = _convert_wide_to_long_format(party_characteristics_df)
    return _calculate_yearly_mean_and_CI(party_characteristics_df)


def get_party_characteristics_yearly_statistics(siteid):
    party_characteristics_df = _prepare_party_characteristics_wide_format(siteid=siteid)
    if party_characteristics_df.empty:
        return _generate_empty_time_series_response()
    party_characteristics_df = _convert_wide_to_long_format(party_characteristics_df)
    return _calculate_yearly_mean_and_CI(party_characteristics_df)


def _prepare_party_characteristics_wide_format(siteids=None, siteid=None):
    party_characteristics_df = get_from_data_source('PARTY_CHARACTERISTICS_DF')
    # Add a 'trail' feature that contains the project site ids (None if observation is not part of project siteids)
    if siteids:
        party_characteristics_df['trail'] = party_characteristics_df['SiteID'].apply(
            lambda lst: next((x for x in lst if x in siteids), None))
    elif siteid:
        party_characteristics_df['trail'] = party_characteristics_df['SiteID'].apply(
            lambda x: siteid if siteid in x else None)
    else:
        raise ValueError("Either siteids or siteid must be provided")
    # keep observations with non-missing 'trail' values
    party_characteristics_df = party_characteristics_df.dropna(subset=['trail'])
    if party_characteristics_df.empty:
        return party_characteristics_df
    return _add_additional_features(party_characteristics_df)


def _convert_wide_to_long_format(df):
    df_long = df.melt(
        id_vars=['date', 'year', 'trail'],
        value_vars=PARTY_CHARACTERISTICS,
        var_name='characteristic',
        value_name='value'
    )
    return df_long


def _add_additional_features(df):
    df = _add_people_per_vehics_feature(df)
    df = _add_year_feature(df)
    return df


def _add_people_per_vehics_feature(df):
    df.loc[:, 'PeoplePerVehics'] = df['PartyPeople'] / df['PartyVehics'].replace(0, np.nan)
    return df


def _add_year_feature(df):
    df.loc[:, 'date'] = pd.to_datetime(df['date'])
    df.loc[:, 'year'] = df['date'].dt.year
    df.loc[:, 'date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df


def _calculate_yearly_mean_and_CI(df):
    grouped = (
        df.groupby(['year', 'characteristic'])
        .agg(mean=('value', 'mean'), std=('value', 'std'), count=('value', 'count'))
        .reset_index()
    )
    grouped = grouped.sort_values(by='year')
    grouped['upper'] = grouped['mean'] + CONFIDENCE_LEVEL * grouped['std'] / np.sqrt(grouped['count'])
    grouped['lower'] = grouped['mean'] - CONFIDENCE_LEVEL * grouped['std'] / np.sqrt(grouped['count'])
    response_data = {"labels": grouped['year'].unique().tolist()}
    for characteristic in grouped['characteristic'].unique():
        characteristic_data = grouped[grouped['characteristic'] == characteristic]
        response_data[characteristic] = {
            "mean": [None if math.isnan(value) else round(value, 2) for value in characteristic_data['mean']],
            "upper_bound": [None if math.isnan(value) else round(value, 2) for value in characteristic_data['upper']],
            "lower_bound": [None if math.isnan(value) else round(value, 2) for value in characteristic_data['lower']]
        }
    return response_data


def _generate_empty_time_series_response():
    return {
        "labels": [],
        **{char: {"mean": [], "upper_bound": [], "lower_bound": []} for char in PARTY_CHARACTERISTICS}
    }
