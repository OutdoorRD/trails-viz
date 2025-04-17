from trailsvizapi.repository.prepare_data import get_from_data_source
from trailsvizapi.repository.projects_and_sites import get_project_sites


SURVEY_START = 'PartyPeople'


def get_annual_chatbot_response_counts(project):
    project_sites = get_project_sites(project)
    siteids = set(project_sites['siteid'].unique())
    chatbot_response_df = _prepare_chatbot_response_data(siteids=siteids)
    if chatbot_response_df.empty:
        return []
    # Group by year and trail, then count rows
    group_counts = chatbot_response_df.groupby(['year', 'trail']).size()
    result = []
    for (year, trail), count in group_counts.items():
        result.append({
            'year': year,
            'trail': trail,
            'count': count
        })
    return result


def _prepare_chatbot_response_data(siteids=None):
    chatbot_response_df = get_from_data_source('CHATBOT_DATA_DF').copy()
    # Add a 'trail' feature that contains the project site ids (None if observation is not part of project siteids)
    if siteids:
        chatbot_response_df['trail'] = chatbot_response_df['SiteID'].apply(
            lambda lst: next((x for x in lst if x in siteids), None))
    # keep observations with non-missing 'trail' values and answer to first survey question
    chatbot_response_df = chatbot_response_df.dropna(subset=['trail', 'PartyPeople'])
    if chatbot_response_df.empty:
        return chatbot_response_df
    chatbot_response_df = chatbot_response_df[['trail', 'year']]
    return chatbot_response_df
