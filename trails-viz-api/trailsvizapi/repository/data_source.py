from trailsvizapi.repository.prepare_data import get_from_data_source


def get_data_source_readme(source):
    data_source_readme_cache = get_from_data_source('DATA_SOURCE_README')
    return data_source_readme_cache[source.lower()]
