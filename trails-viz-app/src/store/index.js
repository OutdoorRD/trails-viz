import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

const state = {
  allProjects: {},
  projectCodeToName: {},
  selectedProjectName: '',
  selectedProjectCode: '',
  selectedProjectDataSources: [],
  projectSites: {},
  selectedSite: '',
  vizMode: '',
  censusTract: '',
  comparingSite: '',
  loggedInUser: 'anon',
  authHeader: 'anon',
  userRole: 'anon',
  selectedSource: '',
  yearRange: [],
  visibleTabGroup: 'project-info',
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
  setSelectedProjectDataSources(state, selectedProjectDataSources) {
    state.selectedProjectDataSources = selectedProjectDataSources
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
  setLoggedInUser(state, loggedInUser) {
    state.loggedInUser = loggedInUser;
  },
  setAuthHeader(state, authHeader) {
    state.authHeader = authHeader;
  },
  setUserRole(state, userRole) {
    state.userRole = userRole;
  },
  clearSelectedProjectData(state) {
    state.selectedProjectName = '';
    state.selectedProjectCode = '';
    state.selectedProjectDataSources = [];
    state.projectSites = {};
    state.selectedSite = '';

    state.annualEstimates = [];
    state.monthlyEstimates = [];

    state.monthlyVisitation = [];
    state.weeklyVisitation = [];

    state.homeLocations = [];
  },
  setSelectedSource(state, selectedSource) {
    state.selectedSource = selectedSource;
  },
  setYearRange(state, range) {
    state.yearRange = range;
  },
  setVisibleTabGroup(state, newTabGroup) {
    state.visibleTabGroup = newTabGroup;
  },
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
  setSelectedProjectDataSources(context, selectedProjectDataSources) {
    context.commit('setSelectedProjectDataSources', selectedProjectDataSources)
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
  setLoggedInUser(context, loggedInUser) {
    context.commit('setLoggedInUser', loggedInUser)
  },
  setAuthHeader(context, authHeader) {
    context.commit('setAuthHeader', authHeader)
  },
  setUserRole(context, userRole) {
    context.commit('setUserRole', userRole)
  },
  clearSelectedProjectData(context) {
    context.commit('clearSelectedProjectData')
  },
  setSelectedSource(context, selectedSource) {
    context.commit('setSelectedSource', selectedSource);
  },
  setYearRange({ commit }, range) {
    commit('setYearRange', range);
  },
  setVisibleTabGroup({ commit }, newTabGroup) {
    commit('setVisibleTabGroup', newTabGroup);
  },
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
  getSelectedProjectDataSources(state) {
    return state.selectedProjectDataSources
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
  },
  getLoggedInUser(state) {
    return state.loggedInUser
  },
  getAuthHeader(state) {
    return state.authHeader
  },
  getUserRole(state) {
    return state.userRole
  },
  getSelectedSource(state) {
    return state.selectedSource;
  },
  getYearRange: (state) => state.yearRange,
  getVisibleTabGroup: (state) => state.visibleTabGroup,
};

const store = new Vuex.Store({
  state,
  mutations,
  actions,
  getters
});

export default store;
