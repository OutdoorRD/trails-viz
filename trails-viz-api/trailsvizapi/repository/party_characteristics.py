from flask import Response, jsonify
from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.projects_and_sites import get_project_sites
import pandas as pd
import numpy as np

CONFIDENCE_LEVEL = 1.96


def get_project_party_characteristics(project, characteristic):
    party_characteristics_df_long = _prep_chatbot_project_long_df(project=project, characteristic=characteristic)
    if not party_characteristics_df_long:
        return Response(status=204)
    response_data = party_characteristics_df_long.to_json(orient='records')
    return Response(response_data, status=200, mimetype='application/json')


def get_party_characteristics(siteid, characteristic):
    party_characteristics_df_long = _prep_chatbot_site_long_df(siteid=siteid, characteristic=characteristic)
    if not party_characteristics_df_long:
        return Response(status=204)
    response_data = party_characteristics_df_long.to_json(orient='records')
    return Response(response_data, status=200, mimetype='application/json')


def get_project_party_characteristics_yearly_statistics(project, characteristic):
    party_characteristics_df_long = _prep_chatbot_project_long_df(project=project, characteristic=characteristic)
    aggregate_data = _prep_chatbot_aggregate_stats(df_long=party_characteristics_df_long,
                                                   characteristic=characteristic)
    if not aggregate_data:
        return Response(status=204)
    return jsonify(aggregate_data), 200


def get_party_characteristics_yearly_statistics(siteid, characteristic):
    party_characteristics_df_long = _prep_chatbot_site_long_df(siteid=siteid, characteristic=characteristic)
    aggregate_data = _prep_chatbot_aggregate_stats(df_long=party_characteristics_df_long,
                                                   characteristic=characteristic)
    if not aggregate_data:
        return Response(status=204)
    return jsonify(aggregate_data), 200


def _prep_chatbot_project_long_df(project, characteristic):
    project_sites = get_project_sites(project)
    siteids = set(project_sites['siteid'].unique())
    party_characteristics_df = get_from_data_source('PARTY_CHARACTERISTICS_DF')
    # Add a 'trail' feature that contains the project assoicated site id.
    # 'trail' value set to None if no site ids in 'SiteID' are not included in the list of project siteids.
    party_characteristics_df['trail'] = party_characteristics_df['SiteID'].apply(
        lambda lst: next((x for x in lst if x in siteids), None))
    # keep observations with non-missing 'trail' values
    party_characteristics_df = party_characteristics_df.dropna(subset=['trail'])
    if party_characteristics_df.empty:
        return None
    if characteristic not in party_characteristics_df.columns:
        party_characteristics_df = _add_additional_features(party_characteristics_df, characteristic)
        if characteristic not in party_characteristics_df.columns:
            return None
    # add year feature
    party_characteristics_df.loc[:, 'year'] = pd.to_datetime(party_characteristics_df['date']).dt.year
    party_characteristics_df_long = party_characteristics_df.melt(
        id_vars=['date', 'year', 'trail'],
        value_vars=[characteristic],
        var_name='characteristic',
        value_name='value'
    )
    party_characteristics_df_long = party_characteristics_df_long.dropna(subset=['date', 'year', 'trail', 'value'])
    if party_characteristics_df_long.empty:
        return None


def _prep_chatbot_site_long_df(siteid, characteristic):
    party_characteristics_df = get_from_data_source('PARTY_CHARACTERISTICS_DF')
    # Add a 'trail' feature that contains the given siteid.
    # 'trail' value set to None if 'SiteID' does not include siteid.
    party_characteristics_df['trail'] = party_characteristics_df['SiteID'].apply(
        lambda x: siteid if siteid in x else None)
    # keep observations with non-missing 'trail' values
    party_characteristics_df = party_characteristics_df.dropna(subset=['trail'])
    if party_characteristics_df.empty:
        return None
    if characteristic not in party_characteristics_df.columns:
        party_characteristics_df = _add_additional_features(party_characteristics_df, characteristic)
        if characteristic not in party_characteristics_df.columns:
            return None
    # add year feature
    party_characteristics_df.loc[:, 'year'] = pd.to_datetime(party_characteristics_df['date']).dt.year
    party_characteristics_df_long = party_characteristics_df.melt(
        id_vars=['date', 'year', 'trail'],
        value_vars=[characteristic],
        var_name='characteristic',
        value_name='value'
    )
    party_characteristics_df_long = party_characteristics_df_long.dropna(subset=['date', 'year', 'trail', 'value'])
    if party_characteristics_df_long.empty:
        return None


def _prep_chatbot_aggregate_stats(df_long, characteristic):
    if not df_long:
        return None
    grouped = (
        df_long.groupby(['year', 'characteristic'])
        .agg(mean=('value', 'mean'), std=('value', 'std'), count=('value', 'count'))
        .reset_index()
    )
    if grouped.empty:
        return None
    grouped = grouped.sort_values(by='year')
    grouped['upper'] = grouped['mean'] + CONFIDENCE_LEVEL * grouped['std'] / np.sqrt(grouped['count'])
    grouped['lower'] = grouped['mean'] - CONFIDENCE_LEVEL * grouped['std'] / np.sqrt(grouped['count'])
    response_data = {
        "years": grouped['year'].unique().tolist(),
        characteristic: {
            "mean": grouped.loc[grouped['characteristic'] == characteristic, 'mean'].round(2).tolist(),
            "upper_bound": grouped.loc[grouped['characteristic'] == characteristic, 'upper'].round(2).tolist(),
            "lower_bound": grouped.loc[grouped['characteristic'] == characteristic, 'lower'].round(2).tolist()
        }
    }
    return response_data


def _add_additional_features(df, feature):
    if feature == 'PeoplePerVehics':
        if 'PartyPeople' in df.columns and 'PartyVehics' in df.columns:
            df.loc[:, 'PeoplePerVehics'] = df['PartyPeople'] / df['PartyVehics'].replace(0, np.nan)
    return df
