export const constants = {
  COLORS: {
    MODELLED: '#1c3dc8',
    FLICKR: '#d8021f',
    INSTA: '#9620e5',
    TWITTER: '#2b7782',
    WTA: '#0ab652',
    ON_SITE: '#ffe702',
    COMPARE_MODELLED: '#fb9205',
    COMPARE_FLICKR: '#c9c9c4',
    COMPARE_INSTA: '#f90dc3',
    COMPARE_TWITTER: '#12fbf2',
    COMPARE_WTA: '#ff0000',
    COMPARE_ON_SITE: '#ff6400',
  }
};

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
