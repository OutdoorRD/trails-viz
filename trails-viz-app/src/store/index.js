import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

const state = {
  allProjects: [],
  selectedProject: '',
  projectSites: {},
  selectedSite: '',

  annualEstimates: [],
  monthlyEstimates: [],

  monthlyVisitation: [],
  weeklyVisitation: [],

  comparingSite: '',
  comparingSiteAnnualEstimates: [],
  comparingSiteMonthlyEstimates: [],
  comparingSiteMonthlyVisitation: [],
  comparingSiteWeeklyVisitation: [],

  homeLocations: [],
  comparingHomeLocations: [],
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
  setAnnualEstimates(state, annualEstimates) {
    state.annualEstimates = annualEstimates;
  },
  setMonthlyEstimates(state, monthlyEstimates) {
    state.monthlyEstimates = monthlyEstimates;
  },
  setMonthlyVisitation(state, monthlyVisitation) {
    state.monthlyVisitation = monthlyVisitation;
  },
  setWeeklyVisitation(state, weeklyVisitation) {
    state.weeklyVisitation = weeklyVisitation;
  },
  setComparingSite(state, comparingSite) {
    state.comparingSite = comparingSite;
  },
  setComparingSiteAnnualEstimates(state, comparingSiteAnnualEstimates) {
    state.comparingSiteAnnualEstimates = comparingSiteAnnualEstimates;
  },
  setComparingSiteMonthlyEstimates(state, comparingSiteMonthlyEstimates) {
    state.comparingSiteMonthlyEstimates = comparingSiteMonthlyEstimates;
  },
  setComparingSiteMonthlyVisitation(state, comparingSiteMonthlyVisitation) {
    state.comparingSiteMonthlyVisitation = comparingSiteMonthlyVisitation;
  },
  setComparingSiteWeeklyVisitation(state, comparingSiteWeeklyVisitation) {
    state.comparingSiteWeeklyVisitation = comparingSiteWeeklyVisitation;
  },
  setHomeLocations(state, homeLocations) {
    state.homeLocations = homeLocations;
  },
  setComparingHomeLocations(state, comparingHomeLocations) {
    state.comparingHomeLocations = comparingHomeLocations;
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
  setAnnualEstimates(context, annualEstimates) {
    context.commit('setAnnualEstimates', annualEstimates)
  },
  setMonthlyEstimates(context, monthlyEstimates) {
    context.commit('setMonthlyEstimates', monthlyEstimates)
  },
  setMonthlyVisitation(context, monthlyVisitation) {
    context.commit('setMonthlyVisitation', monthlyVisitation)
  },
  setWeeklyVisitation(context, weeklyVisitation) {
    context.commit('setWeeklyVisitation', weeklyVisitation)
  },
  setComparingSite(context, comparingSite) {
    context.commit('setComparingSite', comparingSite)
  },
  setComparingSiteAnnualEstimates(context, comparingSiteAnnualEstimates) {
    context.commit('setComparingSiteAnnualEstimates', comparingSiteAnnualEstimates)
  },
  setComparingSiteMonthlyEstimates(context, comparingSiteMonthlyEstimates) {
    context.commit('setComparingSiteMonthlyEstimates', comparingSiteMonthlyEstimates)
  },
  setComparingSiteMonthlyVisitation(context, comparingSiteMonthlyVisitation) {
    context.commit('setComparingSiteMonthlyVisitation', comparingSiteMonthlyVisitation)
  },
  setComparingSiteWeeklyVisitation(context, comparingSiteWeeklyVisitation) {
    context.commit('setComparingSiteWeeklyVisitation', comparingSiteWeeklyVisitation)
  },
  setHomeLocations(context, homeLocations) {
    context.commit('setHomeLocations', homeLocations)
  },
  setComparingHomeLocations(context, comparingHomeLocations) {
    context.commit('setComparingHomeLocations', comparingHomeLocations)
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
  getAnnualEstimates(state) {
    return state.annualEstimates
  },
  getMonthlyEstimates(state) {
    return state.monthlyEstimates
  },
  getMonthlyVisitation(state) {
    return state.monthlyVisitation
  },
  getWeeklyVisitation(state) {
    return state.weeklyVisitation
  },
  getComparingSite(state) {
    return state.comparingSite
  },
  getComparingSiteAnnualEstimates(state) {
    return state.comparingSiteAnnualEstimates
  },
  getComparingSiteMonthlyEstimates(state) {
    return state.comparingSiteMonthlyEstimates
  },
  getComparingSiteMonthlyVisitation(state) {
    return state.comparingSiteMonthlyVisitation
  },
  getComparingSiteWeeklyVisitation(state) {
    return state.comparingSiteWeeklyVisitation
  },
  getHomeLocations(state) {
    return state.homeLocations
  },
  getComparingHomeLocations(state) {
    return state.comparingHomeLocations
  }
};

const store = new Vuex.Store({
  state,
  mutations,
  actions,
  getters
});

export default store;
