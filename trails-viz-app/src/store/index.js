export const store = {
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

  setAllProjects(allProjects) {
    this.allProjects = allProjects;
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
  setMonthlyVisitation(monthlyVisitation) {
    this.monthlyVisitation = monthlyVisitation;
  },
  setWeeklyVisitation(weeklyVisitation) {
    this.weeklyVisitation = weeklyVisitation;
  },
  setComparingSite(comparingSite) {
    this.comparingSite = comparingSite;
  },
  setComparingSiteAnnualEstimates(comparingSiteAnnualEstimates) {
    this.comparingSiteAnnualEstimates = comparingSiteAnnualEstimates;
  },
  setComparingSiteMonthlyEstimates(comparingSiteMonthlyEstimates) {
    this.comparingSiteMonthlyEstimates = comparingSiteMonthlyEstimates;
  },
  setComparingSiteMonthlyVisitation(comparingSiteMonthlyVisitation) {
    this.comparingSiteMonthlyVisitation = comparingSiteMonthlyVisitation;
  },
  setComparingSiteWeeklyVisitation(comparingSiteWeeklyVisitation) {
    this.comparingSiteWeeklyVisitation = comparingSiteWeeklyVisitation;
  },
  clearSelectedProjectData() {
    this.selectedProject = '';
    this.projectSites = {};
    this.selectedSite = '';

    this.annualEstimates = [];
    this.monthlyEstimates = [];

    this.monthlyVisitation = [];
    this.weeklyVisitation = [];
  }
};
