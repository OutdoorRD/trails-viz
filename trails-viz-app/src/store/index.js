import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

const state = {
  allProjects: undefined,
  projectCodeToName: undefined,
  selectedProjectName: '',
  selectedProjectCode: '',
  projectSites: {},
  selectedSite: '',
  vizMode: '',
  censusTract: '',
  comparingSite: '',
};

const mutations = {
  setAllProjects(state, allProjects) {
    state.allProjects = allProjects;
  },
  setProjectCodeToName(state, projectCodeToName) {
    state.projectCodeToName = projectCodeToName;
  },
  setSelectedProjectName(state, projectName) {
    state.selectedProjectName = projectName
  },
  setSelectedProjectCode(state, projectCode) {
    state.selectedProjectCode = projectCode
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
  setCensusTract(state, censusTract) {
    state.censusTract = censusTract
  },
  setComparingSite(state, comparingSite) {
    state.comparingSite = comparingSite;
  },
  clearSelectedProjectData(state) {
    state.selectedProjectName = '';
    state.selectedProjectCode = '';
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
  setProjectCodeToName(context, projectCodeToName) {
    context.commit('setProjectCodeToName', projectCodeToName)
  },
  setSelectedProjectName(context, projectName) {
    context.commit('setSelectedProjectName', projectName)
  },
  setSelectedProjectCode(context, projectCode) {
    context.commit('setSelectedProjectCode', projectCode)
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
  setCensusTract(context, censusTract) {
    context.commit('setCensusTract', censusTract)
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
  getProjectCodeToName(state) {
    return state.projectCodeToName
  },
  getSelectedProjectName(state) {
    return state.selectedProjectName
  },
  getSelectedProjectCode(state) {
    return state.selectedProjectCode
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
  getCensusTract(state) {
    return state.censusTract
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
