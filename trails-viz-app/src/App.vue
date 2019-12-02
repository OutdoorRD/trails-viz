<template>
  <b-container fluid id="app">
    <top-bar v-on:project-selected="sendProjectSelectedEventToMap" v-on:site-selected="sendSiteSelectedEventToMap" class="top-bar"></top-bar>
    <landing-page id="landing-page" class="landing-page" v-on:project-selected="sendProjectSelectedEventToMap"/>
    <b-row no-gutters class="app-container" id="visualization-zone">
      <b-col sm="6" class="map-col">
        <map-div ref="map-div" id="mapDiv" v-on:site-selected="sendRenderPlotEvents" v-on:compare-activated="sendCompareSites"></map-div>
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
              <b-tab title="Home Locations">
                <b-tabs content-class="mt-3" nav-item-class="text info" fill>
                  <b-tab title="Info" active>
                    <info-viewer ref="home-locations-info"></info-viewer>
                  </b-tab>
                  <b-tab title="Tree Map">
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
  </b-container>
</template>

<script>
import MapDiv from "@/components/MapDiv";
import TopBar from "@/components/TopBar";
import BarGraph from "@/components/BarGraph";
import TimeSeries from "@/components/TimeSeries";
import HomeLocations from "@/components/HomeLocations";
import HomeLocationsMap from "@/components/HomeLocationsMap";
import InfoViewer from "@/components/InfoViewer";
import LandingPage from "./components/LandingPage";
import DemographicsSummary from "./components/DemographicsSummary";

import axios from "axios";
import {VIZ_MODES} from "./store/constants";

export default {
  name: 'app',
  data: function() {
    return {
      trailName: '',
      comparingTrailName: ''
    }
  },
  components: {
    InfoViewer,
    DemographicsSummary,
    LandingPage,
    HomeLocationsMap,
    HomeLocations,
    TimeSeries,
    BarGraph,
    TopBar,
    MapDiv
  },
  mounted() {
    let self = this;
    axios.get(self.$apiEndpoint + '/projects')
      .then(response => self.$store.dispatch('setAllProjects', response.data));
    axios.get(self.$apiEndpoint + '/sites/censusTract')
      .then(response => self.$store.dispatch('setCensusTract', response.data));
  },
  methods: {
    sendProjectSelectedEventToMap: function () {
      let store = this.$store;
      let projectName = store.getters.getSelectedProjectName;
      let projectCode = store.getters.getSelectedProjectCode;

      this.trailName = 'All Sites in ' + projectName;
      store.dispatch('setSelectedProjectName', projectName);
      store.dispatch('setSelectedProjectCode', projectCode);
      store.dispatch('setSelectedSite', {'trailName': projectName, setStyle: x => x}); // a dummy set style method which does nothing

      store.dispatch('setVizMode', VIZ_MODES.PROJECT);
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
    sendSiteSelectedEventToMap: function(trailName) {
      this.$refs['map-div'].selectSite(trailName)
    },
    sendRenderPlotEvents: function () {
      this.trailName = this.$store.getters.getSelectedSite['trailName'];
      this.comparingTrailName = '';

      this.$store.dispatch('setVizMode', VIZ_MODES.SITE);
      this.$refs['bar-graph'].renderDefaultGraph();
      this.$refs['time-series'].renderTimeSeries();
      this.$refs['home-locations'].renderTreeMap();
      this.$refs['home-locations-map'].renderHomeLocationsMap();
      this.$refs['demographics-summary'].renderDemographicsSummary();
    },
    sendCompareSites: function () {
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
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    padding: 0;
    height: 100vh;
  }

  .top-bar {
    height: 60px;
  }

  .landing-page {
    height: calc(100vh - 60px);
  }

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
