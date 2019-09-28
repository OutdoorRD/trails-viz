import Vue from 'vue'
import axios from 'axios'

export const store = {
  allProjects: [],
  selectedProject: '',
  projectSites: {},
  selectedSite: '',
  fetchAllProjects() {
    axios.get(Vue.prototype.$apiEndpoint + '/projects')
      .then(response => this.allProjects = response.data);
  },
  setSelectedProject(project) {
    this.selectedProject = project
  },
  setProjectSites(projectSites) {
    this.projectSites = projectSites
  },
  setSelectedSite(site) {
    this.selectedSite = site
  }
};
