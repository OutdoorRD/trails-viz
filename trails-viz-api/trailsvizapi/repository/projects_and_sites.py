from trailsvizapi.repository.prepare_data import get_from_data_source


def get_project_sites(project_group):
    allsites = get_from_data_source('ALLSITES_DF')
    project_sites = allsites[allsites['Prjct_code'].str.contains(project_group)]
    return project_sites


def get_project_from_site(siteid):
    allsites = get_from_data_source('ALLSITES_DF')
    site = allsites[allsites['siteid'] == siteid]
    project_code = site[['Prjct_code']].iat[0, 0]
    project_list = [code.strip() for code in project_code.split(',')
                    ] if ',' in project_code else [project_code.strip()]
    return project_list


def get_project_readme(readme_type, project):
    project_readme_cache = get_from_data_source('PROJECT_README')
    if readme_type == 'VISITS':
        return project_readme_cache[project + '_VISITS']
    else:
        return project_readme_cache[project]
