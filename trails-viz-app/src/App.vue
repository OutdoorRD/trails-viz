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
                <site-info ref="site-info"></site-info>
              </b-tab>
              <b-tab title="Bar Graph">
                <bar-graph ref="bar-graph"></bar-graph>
              </b-tab>
              <b-tab title="Time Series">
                <time-series ref="time-series"></time-series>
              </b-tab>
              <b-tab title="Home Locations">
                <home-locations ref="home-locations"></home-locations>
              </b-tab>
              <b-tab title="Home Locations Map" v-on:update:active="activateHomeLocationsMap">
                <home-locations-map ref="home-locations-map"></home-locations-map>
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

import axios from "axios";
import {VIZ_MODES} from "./store/constants";
import SiteInfo from "./components/SiteInfo";
import LandingPage from "./components/LandingPage";

export default {
  name: 'app',
  data: function() {
    return {
      trailName: '',
      comparingTrailName: ''
    }
  },
  components: {
    LandingPage,
    SiteInfo,
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
      let project = store.getters.getSelectedProject;

      this.trailName = 'All Sites in ' + project;
      store.dispatch('setSelectedProject', project);
      store.dispatch('setSelectedSite', {'trailName': project, setStyle: x => x}); // a dummy set style method which does nothing

      store.dispatch('setVizMode', VIZ_MODES.PROJECT);
      this.$refs['map-div'].renderProjectSites();

      // render plots on project level
      this.$refs['bar-graph'].renderDefaultGraph();
      this.$refs['time-series'].renderTimeSeries();
      this.$refs['home-locations'].renderTreeMap();
      this.$refs['home-locations-map'].renderHomeLocationsMap();
      this.$refs['site-info'].renderProjectInfo();
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
