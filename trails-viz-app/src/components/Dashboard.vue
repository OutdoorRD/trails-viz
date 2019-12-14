<template>
  <b-row no-gutters class="app-container">
    <b-col sm="6" class="map-col">
      <map-div ref="map-div" id="mapDiv" v-on:site-selected="renderSiteLevelPlots" v-on:compare-activated="renderComparisionPlots"></map-div>
    </b-col>
    <b-col sm="6" class="charts-col">
      <b-row no-gutters>
        <b-col sm="12">
          <h3>{{trailName}} <span v-show="comparingTrailName">vs {{comparingTrailName}}</span></h3>
        </b-col>
      </b-row>
      <b-row no-gutters v-show="trailName">
        <b-col sm="12">
          <b-tabs content-class="mt-3" nav-item-class="text info" fill>
            <b-tab title="Info" active>
              <info-viewer ref="project-info"></info-viewer>
            </b-tab>
            <b-tab title="Visitation">
              <b-tabs content-class="mt-3" nav-item-class="text info" fill>
                <b-tab title="Info" active>
                  <info-viewer ref="visitation-info"></info-viewer>
                </b-tab>
                <b-tab title="Bar Graph">
                  <bar-graph ref="bar-graph"></bar-graph>
                </b-tab>
                <b-tab title="Time Series">
                  <time-series ref="time-series"></time-series>
                </b-tab>
              </b-tabs>
            </b-tab>
            <b-tab title="Visitor Characteristics">
              <b-tabs content-class="mt-3" nav-item-class="text info" fill>
                <b-tab title="Info" active>
                  <info-viewer ref="home-locations-info"></info-viewer>
                </b-tab>
                <b-tab title="Home Counties">
                  <home-locations ref="home-locations"></home-locations>
                </b-tab>
                <b-tab title="Home Locations Map" v-on:update:active="activateHomeLocationsMap">
                  <home-locations-map ref="home-locations-map"></home-locations-map>
                </b-tab>
                <b-tab title="Demographics">
                  <demographics-summary ref="demographics-summary"></demographics-summary>
                </b-tab>
              </b-tabs>
            </b-tab>
          </b-tabs>
        </b-col>
      </b-row>
    </b-col>
  </b-row>
</template>

<script>
  import axios from "axios";

  import MapDiv from "../components/MapDiv";
  import BarGraph from "../components/BarGraph";
  import TimeSeries from "../components/TimeSeries";
  import HomeLocations from "../components/HomeLocations";
  import HomeLocationsMap from "../components/HomeLocationsMap";
  import InfoViewer from "../components/InfoViewer";
  import DemographicsSummary from "../components/DemographicsSummary";

  import {VIZ_MODES} from "../store/constants";

  export default {
    name: "Dashboard",
    data: function() {
      return {
        trailName: '',
        comparingTrailName: ''
      }
    },
    mounted() {
      // This part of code has been duplicated from App
      // because in case of hitting the project URL directly
      // app won't load in time to have these global variables populated
      let self = this;
      if (self.$store.getters.getAllProjects === undefined) {
        axios.get(self.$apiEndpoint + '/projects')
          .then(response => {
            let allProjects = response.data;
            let projectCodeToName = {};
            for (let [name, code] of Object.entries(allProjects)) {
              projectCodeToName[code] = name
            }
            self.$store.dispatch('setAllProjects', allProjects);
            self.$store.dispatch('setProjectCodeToName', projectCodeToName);

            this.renderProjectLevelPlots();
          });
      } else {
        this.renderProjectLevelPlots();
      }
    },
    components: {
      InfoViewer,
      DemographicsSummary,
      HomeLocationsMap,
      HomeLocations,
      TimeSeries,
      BarGraph,
      MapDiv
    },
    methods: {
      renderProjectLevelPlots: function() {
        this.$store.dispatch('setVizMode', VIZ_MODES.PROJECT);

        let store = this.$store;
        let projectCode = this.$route.params.project;
        let projectName = store.getters.getProjectCodeToName[projectCode];
        this.$store.dispatch('setSelectedProjectCode', projectCode);
        this.$store.dispatch('setSelectedProjectName', projectName);

        this.trailName = 'All Sites in ' + projectName;
        store.dispatch('setSelectedSite', {'trailName': projectName, setStyle: x => x}); // a dummy set style method which does nothing

        this.$refs['map-div'].renderProjectSites();

        // render plots on project level
        this.$refs['bar-graph'].renderDefaultGraph();
        this.$refs['time-series'].renderTimeSeries();
        this.$refs['home-locations'].renderTreeMap();
        this.$refs['home-locations-map'].renderHomeLocationsMap();
        this.$refs['project-info'].renderInfo('project');
        this.$refs['visitation-info'].renderInfo('visitation');
        this.$refs['home-locations-info'].renderInfo('homeLocations');
        this.$refs['demographics-summary'].renderDemographicsSummary();

      },
      renderSiteLevelPlots: function () {
        this.trailName = this.$store.getters.getSelectedSite['trailName'];
        this.comparingTrailName = '';

        this.$store.dispatch('setVizMode', VIZ_MODES.SITE);
        this.$refs['bar-graph'].renderDefaultGraph();
        this.$refs['time-series'].renderTimeSeries();
        this.$refs['home-locations'].renderTreeMap();
        this.$refs['home-locations-map'].renderHomeLocationsMap();
        this.$refs['demographics-summary'].renderDemographicsSummary();
      },
      renderComparisionPlots: function () {
        this.$store.dispatch('setVizMode', VIZ_MODES.COMPARE);
        this.comparingTrailName = this.$store.getters.getComparingSite['trailName'];
        this.$refs['bar-graph'].renderDefaultGraph();
        this.$refs['time-series'].renderTimeSeries();
        this.$refs['home-locations'].renderTreeMap();
      },
      activateHomeLocationsMap: function (event) {
        // The event here is a boolean variable which tell if the
        // tab was activated (true) or deactivated (false)
        if (event) {
          this.$refs['home-locations-map'].activateHomeLocationsMap()
        }
      }
    }
  }
</script>

<style scoped>

  .app-container {
    height: calc(100vh - 60px);
  }

  .map-col {
    padding: 4px 4px 4px 4px !important;
  }

  .charts-col {
    padding: 4px 4px 4px 4px !important;
  }
</style>
