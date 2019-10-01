import Vue from 'vue'
import axios from 'axios'

export const store = {
  allProjects: [],
  selectedProject: '',
  projectSites: {},
  selectedSite: '',

  annualEstimates: [],
  monthlyEstimates: [],
  weeklyEstimates: [],

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
  },
  setAnnualEstimates(annualEstimates) {
    this.annualEstimates = annualEstimates;
  },
  setMonthlyEstimates(monthlyEstimates) {
    this.monthlyEstimates = monthlyEstimates;
  },
  setWeeklyEstimates(weeklyEstimates) {
    this.weeklyEstimates = weeklyEstimates;
  }
};
