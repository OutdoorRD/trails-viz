import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

const state = {
  allProjects: [],
  selectedProject: '',
  projectSites: {},
  selectedSite: '',
  vizMode: '',

  comparingSite: '',
};

const mutations = {
  setAllProjects(state, allProjects) {
    state.allProjects = allProjects;
  },
  setSelectedProject(state, project) {
    state.selectedProject = project
  },
  setProjectSites(state, projectSites) {
    state.projectSites = projectSites
  },
  setSelectedSite(state, site) {
    state.selectedSite = site
  },
  setVizMode(state, vizMode) {
    state.vizMode = vizMode
  },
  setComparingSite(state, comparingSite) {
    state.comparingSite = comparingSite;
  },
  clearSelectedProjectData(state) {
    state.selectedProject = '';
    state.projectSites = {};
    state.selectedSite = '';

    state.annualEstimates = [];
    state.monthlyEstimates = [];

    state.monthlyVisitation = [];
    state.weeklyVisitation = [];

    state.homeLocations = [];
  }
};

const actions = {
  setAllProjects(context, allProjects) {
    context.commit('setAllProjects', allProjects)
  },
  setSelectedProject(context, project) {
    context.commit('setSelectedProject', project)
  },
  setProjectSites(context, projectSites) {
    context.commit('setProjectSites', projectSites)
  },
  setSelectedSite(context, site) {
    context.commit('setSelectedSite', site)
  },
  setVizMode(context, vizMode) {
    context.commit('setVizMode', vizMode)
  },
  setComparingSite(context, comparingSite) {
    context.commit('setComparingSite', comparingSite)
  },
  clearSelectedProjectData(context) {
    context.commit('clearSelectedProjectData')
  }
};

const getters = {
  getAllProjects(state) {
    return state.allProjects
  },
  getSelectedProject(state) {
    return state.selectedProject
  },
  getProjectSites(state) {
    return state.projectSites
  },
  getSelectedSite(state) {
    return state.selectedSite
  },
  getVizMode(state) {
    return state.vizMode
  },
  getComparingSite(state) {
    return state.comparingSite
  }
};

const store = new Vuex.Store({
  state,
  mutations,
  actions,
  getters
});

export default store;
