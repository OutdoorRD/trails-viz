from flask import Response, jsonify
from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.projects_and_sites import get_project_sites
import pandas as pd
import numpy as np

CONFIDENCE_LEVEL = 1.96


def get_project_chatbot_data(project, characteristic):
    chatbot_data_df_long = _prep_chatbot_project_long_df(project=project, characteristic=characteristic)
    if chatbot_data_df_long is None:
        return Response(status=204)
    response_data = chatbot_data_df_long.to_json(orient='records')
    return Response(response_data, status=200, mimetype='application/json')


def get_chatbot_data(siteid, characteristic):
    chatbot_data_df_long = _prep_chatbot_site_long_df(siteid=siteid, characteristic=characteristic)
    if chatbot_data_df_long is None:
        return Response(status=204)
    response_data = chatbot_data_df_long.to_json(orient='records')
    return Response(response_data, status=200, mimetype='application/json')


def get_project_chatbot_data_yearly_statistics(project, characteristic):
    chatbot_data_df_long = _prep_chatbot_project_long_df(project=project, characteristic=characteristic)
    aggregate_data = _prep_chatbot_aggregate_stats(df_long=chatbot_data_df_long,
                                                   characteristic=characteristic)
    if aggregate_data is None:
        return Response(status=204)
    return jsonify(aggregate_data), 200


def get_chatbot_data_yearly_statistics(siteid, characteristic):
    chatbot_data_df_long = _prep_chatbot_site_long_df(siteid=siteid, characteristic=characteristic)
    aggregate_data = _prep_chatbot_aggregate_stats(df_long=chatbot_data_df_long,
                                                   characteristic=characteristic)
    if aggregate_data is None:
        return Response(status=204)
    return jsonify(aggregate_data), 200


def _prep_chatbot_project_long_df(project, characteristic):
    project_sites = get_project_sites(project)
    siteids = set(project_sites['siteid'].unique())
    chatbot_data_df = get_from_data_source('CHATBOT_DATA_DF').copy()
    # Add a 'trail' feature that contains the project assoicated site id.
    # 'trail' value set to None if no site ids in 'SiteID' are not included in the list of project siteids.
    chatbot_data_df['trail'] = chatbot_data_df['SiteID'].apply(
        lambda lst: next((x for x in lst if x in siteids), None))
    # keep observations with non-missing 'trail' values
    chatbot_data_df = chatbot_data_df.dropna(subset=['trail'])
    if chatbot_data_df.empty:
        return None
    if characteristic not in chatbot_data_df.columns:
        chatbot_data_df = _add_additional_features(chatbot_data_df, characteristic)
        if characteristic not in chatbot_data_df.columns:
            return None
    # add year feature
    chatbot_data_df.loc[:, 'year'] = pd.to_datetime(chatbot_data_df['date']).dt.year
    chatbot_data_df_long = chatbot_data_df.melt(
        id_vars=['date', 'year', 'trail'],
        value_vars=[characteristic],
        var_name='characteristic',
        value_name='value'
    )
    chatbot_data_df_long = chatbot_data_df_long.dropna(subset=['date', 'year', 'trail', 'value'])
    if chatbot_data_df_long.empty:
        return None
    return chatbot_data_df_long


def _prep_chatbot_site_long_df(siteid, characteristic):
    chatbot_data_df = get_from_data_source('CHATBOT_DATA_DF').copy()
    # Add a 'trail' feature that contains the given siteid.
    # 'trail' value set to None if 'SiteID' does not include siteid.
    chatbot_data_df['trail'] = chatbot_data_df['SiteID'].apply(
        lambda x: siteid if siteid in x else None)
    # keep observations with non-missing 'trail' values
    chatbot_data_df = chatbot_data_df.dropna(subset=['trail'])
    if chatbot_data_df.empty:
        return None
    if characteristic not in chatbot_data_df.columns:
        chatbot_data_df = _add_additional_features(chatbot_data_df, characteristic)
        if characteristic not in chatbot_data_df.columns:
            return None
    # add year feature
    chatbot_data_df.loc[:, 'year'] = pd.to_datetime(chatbot_data_df['date']).dt.year
    chatbot_data_df_long = chatbot_data_df.melt(
        id_vars=['date', 'year', 'trail'],
        value_vars=[characteristic],
        var_name='characteristic',
        value_name='value'
    )
    chatbot_data_df_long = chatbot_data_df_long.dropna(subset=['date', 'year', 'trail', 'value'])
    if chatbot_data_df_long.empty:
        return None
    return chatbot_data_df_long


def _prep_chatbot_aggregate_stats(df_long, characteristic):
    if df_long is None:
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
    pass
