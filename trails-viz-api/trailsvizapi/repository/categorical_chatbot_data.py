from collections import Counter
from flask import Response, jsonify
from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.projects_and_sites import get_project_sites


def get_project_categorical_chatbot_data(project, characteristic, year_start, year_end):
    """
    Aggregates categorical chatbot data by project.
    Filtering is done by the site's membership in the project.
    """
    df = get_from_data_source('CHATBOT_DATA_DF').copy()
    # Get all siteids for the given project
    project_sites = get_project_sites(project)
    siteids = set(project_sites['siteid'].unique())
    # Create a 'trail' column if any SiteID in the row belongs to the project
    df['trail'] = df['SiteID'].apply(lambda lst: next((x for x in lst if x in siteids), None))
    df = df.dropna(subset=['trail'])
    # If a 'year' column exists, filter by year_start and year_end if provided.
    if 'year' in df.columns:
        if year_start is not None:
            df = df[df['year'] >= int(year_start)]
        if year_end is not None:
            df = df[df['year'] <= int(year_end)]
    if df.empty:
        return Response(status=204)
    counts = _prep_chatbot_aggregate_counts_categorical(df, characteristic)
    if not counts:
        return Response(status=204)
    return jsonify({characteristic: counts}), 200


def get_categorical_chatbot_data(siteid, characteristic, year_start, year_end):
    """
    Aggregates categorical chatbot data for a specific site.
    Filtering is done by ensuring the site is present in the row's SiteID list.
    """
    df = get_from_data_source('CHATBOT_DATA_DF').copy()
    # Set 'trail' to the siteid if the given site is in the list
    df['trail'] = df['SiteID'].apply(lambda lst: siteid if siteid in lst else None)
    df = df.dropna(subset=['trail'])
    # If a 'year' column exists, filter by year_start and year_end if provided.
    if 'year' in df.columns:
        if year_start is not None:
            df = df[df['year'] >= int(year_start)]
        if year_end is not None:
            df = df[df['year'] <= int(year_end)]

    if df.empty:
        return Response(status=204)
    counts = _prep_chatbot_aggregate_counts_categorical(df, characteristic)
    if not counts:
        return Response(status=204)
    return jsonify({characteristic: counts}), 200


def _prep_chatbot_aggregate_counts_categorical(df, characteristic):
    if df is None or df.empty or characteristic not in df.columns:
        return None
    # Drop missing values in the characteristic column
    values = df[characteristic].dropna()
    # Split comma-separated values and flatten the list
    # all_values = values.apply(lambda x: [s.strip() for s in str(x).split(",")])
    flat_values = [item for sublist in values for item in sublist]
    # Count each unique value and sort by count (most frequent first)
    counts = Counter(flat_values)
    sorted_counts = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
    return sorted_counts
