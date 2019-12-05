from trailsvizapi.repository.prepare_data import get_from_data_source


def get_project_sites(project_group):
    allsites = get_from_data_source('ALLSITES_DF')
    project_sites = allsites[allsites['Prjct_code'].str.contains(project_group)]
    return project_sites


def get_project_readme(readme_type, project=None):
    project_readme_cache = get_from_data_source('PROJECT_README')
    if readme_type == 'VISITS':
        return project_readme_cache[project + '_VISITS']
    elif readme_type == 'INFO':
        return project_readme_cache[project]
    else:
        return project_readme_cache[readme_type]
