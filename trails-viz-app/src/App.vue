<template>
  <b-container fluid id="app">
    <top-bar v-on:project-selected="sendProjectSelectedEventToMap" v-on:site-selected="sendSiteSelectedEventToMap"></top-bar>
    <b-row no-gutters>
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
              <b-tab title="Bar Graph" active>
                <bar-graph ref="bar-graph"></bar-graph>
              </b-tab>
              <b-tab title="Time Series">
                <time-series ref="time-series"></time-series>
              </b-tab>
              <b-tab title="Home Locations">
                <home-locations ref="home-locations"></home-locations>
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

import axios from "axios";

export default {
  name: 'app',
  data: function() {
    return {
      trailName: '',
      comparingTrailName: ''
    }
  },
  components: {
    HomeLocations,
    TimeSeries,
    BarGraph,
    TopBar,
    MapDiv
  },
  mounted() {
    let self = this;
    axios.get(this.$apiEndpoint + '/projects')
      .then(response => self.$store.dispatch('setAllProjects', response.data));
  },
  methods: {
    sendProjectSelectedEventToMap: function () {
      let store = this.$store;
      let project = store.getters.getSelectedProject;
      store.dispatch('clearSelectedProjectData');

      this.trailName = 'All Sites in ' + project;
      store.dispatch('setSelectedProject', project);
      store.dispatch('setSelectedSite', {'trailName': project, setStyle: x => x}); // a dummy set style method which does nothing

      this.$refs['map-div'].renderProjectSites();
      this.$refs['bar-graph'].clearBarGraph();
      this.$refs['time-series'].clearTimeSeries();
      this.$refs['home-locations'].clear();


      // render plots on project level
      axios.all([
        axios.get(this.$apiEndpoint + '/projects/' + project + '/annualEstimates'),
        axios.get(this.$apiEndpoint + '/projects/' + project + '/monthlyEstimates'),
        axios.get(this.$apiEndpoint + '/projects/' + project + '/monthlyVisitation'),
        axios.get(this.$apiEndpoint + '/projects/' + project + '/weeklyVisitation'),
        axios.get(this.$apiEndpoint + '/projects/' + project + '/homeLocations'),
      ]).then(axios.spread((annualEstimateRes, monthlyEstimateRes, monthlyVisitationRes, weeklyVisitationRes, homeLocationsRes) => {
        store.dispatch('setAnnualEstimates', annualEstimateRes.data);
        store.dispatch('setMonthlyEstimates', monthlyEstimateRes.data);
        store.dispatch('setMonthlyVisitation', monthlyVisitationRes.data);
        store.dispatch('setWeeklyVisitation', weeklyVisitationRes.data);
        store.dispatch('setHomeLocations', homeLocationsRes.data);
        this.$refs['bar-graph'].renderDefaultGraph();
        this.$refs['time-series'].renderTimeSeries();
        this.$refs['home-locations'].renderTreeMap();
      }))

    },
    sendSiteSelectedEventToMap: function(trailName) {
      this.$refs['map-div'].selectSite(trailName)
    },
    sendRenderPlotEvents: function () {
      // populate the estimates in global store to be used in bar graph and time series
      let store = this.$store;
      let siteid = store.getters.getSelectedSite['siteid'];
      this.trailName = store.getters.getSelectedSite['trailName'];
      this.comparingTrailName = '';
      axios.all([
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/annualEstimates'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/monthlyEstimates'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/monthlyVisitation'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/weeklyVisitation'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/homeLocations'),
      ]).then(axios.spread((annualEstimateRes, monthlyEstimateRes, monthlyVisitationRes, weeklyVisitationRes, homeLocationsRes) => {
        store.dispatch('setAnnualEstimates', annualEstimateRes.data);
        store.dispatch('setMonthlyEstimates', monthlyEstimateRes.data);
        store.dispatch('setMonthlyVisitation', monthlyVisitationRes.data);
        store.dispatch('setWeeklyVisitation', weeklyVisitationRes.data);
        store.dispatch('setHomeLocations', homeLocationsRes.data);
        this.$refs['bar-graph'].renderDefaultGraph();
        this.$refs['time-series'].renderTimeSeries();
        this.$refs['home-locations'].renderTreeMap();
      }))
    },
    sendCompareSites: function () {
      let store = this.$store;
      let siteid = store.getters.getComparingSite['siteid'];
      this.comparingTrailName = store.getters.getComparingSite['trailName'];
      axios.all([
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/annualEstimates'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/monthlyEstimates'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/monthlyVisitation'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/weeklyVisitation'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/homeLocations'),
      ]).then(axios.spread((annualEstimateRes, monthlyEstimateRes, monthlyVisitationRes, weeklyVisitationRes, homeLocationsRes) => {
        store.dispatch('setComparingSiteAnnualEstimates', annualEstimateRes.data);
        store.dispatch('setComparingSiteMonthlyEstimates', monthlyEstimateRes.data);
        store.dispatch('setComparingSiteMonthlyVisitation', monthlyVisitationRes.data);
        store.dispatch('setComparingSiteWeeklyVisitation', weeklyVisitationRes.data);
        store.dispatch('setComparingHomeLocations', homeLocationsRes.data);
        this.$refs['bar-graph'].renderSelectedGraph();
        this.$refs['time-series'].renderTimeSeries();
        this.$refs['home-locations'].renderTreeMap();
      }))
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
  }

  .map-col {
    padding: 4px 4px 4px 4px !important;
  }
  .charts-col {
    padding: 4px 4px 4px 4px !important;
  }
</style>
