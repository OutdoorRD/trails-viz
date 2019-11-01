from trailsvizapi.repository.prepare_data import get_from_data_source


def get_project_sites(project_group):
    allsites = get_from_data_source('ALLSITES_DF')
    project_sites = allsites[allsites['Prjct_code'].str.contains(project_group)]
    return project_sites
