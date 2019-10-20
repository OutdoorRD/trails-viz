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

              </b-tab>
            </b-tabs>
          </b-col>
        </b-row>
      </b-col>
    </b-row>
    <b-row no-gutters>
      <b-col sm="12">
        <footer-bar></footer-bar>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import MapDiv from "@/components/MapDiv";
import TopBar from "@/components/TopBar";
import BarGraph from "@/components/BarGraph";
import TimeSeries from "@/components/TimeSeries";
import FooterBar from "@/components/FooterBar";

import {store} from "./store";
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
    FooterBar,
    TimeSeries,
    BarGraph,
    TopBar,
    MapDiv
  },
  mounted() {
    axios.get(this.$apiEndpoint + '/projects')
      .then(response => store.setAllProjects(response.data));
  },
  methods: {
    sendProjectSelectedEventToMap: function () {
      this.$refs['map-div'].renderProjectSites();
      this.$refs['bar-graph'].clearBarGraph();
      this.$refs['time-series'].clearTimeSeries();
      store.clearSelectedProjectData();
    },
    sendSiteSelectedEventToMap: function(trailName) {
      this.$refs['map-div'].selectSite(trailName)
    },
    sendRenderPlotEvents: function () {
      // populate the estimates in global store to be used in bar graph and time series
      let siteid = store.selectedSite['siteid'];
      this.trailName = store.selectedSite['trailName'];
      this.comparingTrailName = '';
      axios.all([
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/annualEstimates'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/monthlyEstimates'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/monthlyVisitation'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/weeklyVisitation'),
      ]).then(axios.spread((annualEstimateRes, monthlyEstimateRes, monthlyVisitationRes, weeklyVisitationRes) => {
        store.setAnnualEstimates(annualEstimateRes.data);
        store.setMonthlyEstimates(monthlyEstimateRes.data);
        store.setMonthlyVisitation(monthlyVisitationRes.data);
        store.setWeeklyVisitation(weeklyVisitationRes.data);
        this.$refs['bar-graph'].renderDefaultGraph();
        this.$refs['time-series'].renderTimeSeries();
      }))
    },
    sendCompareSites: function () {
      let siteid = store.comparingSite['siteid'];
      this.comparingTrailName = store.comparingSite['trailName'];
      axios.all([
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/annualEstimates'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/monthlyEstimates'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/monthlyVisitation'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/weeklyVisitation'),
      ]).then(axios.spread((annualEstimateRes, monthlyEstimateRes, monthlyVisitationRes, weeklyVisitationRes) => {
        store.setComparingSiteAnnualEstimates(annualEstimateRes.data);
        store.setComparingSiteMonthlyEstimates(monthlyEstimateRes.data);
        store.setComparingSiteMonthlyVisitation(monthlyVisitationRes.data);
        store.setComparingSiteWeeklyVisitation(weeklyVisitationRes.data);
        this.$refs['bar-graph'].renderSelectedGraph();
        this.$refs['time-series'].renderTimeSeries();
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
    padding: 4px 2px 4px 4px !important;
  }
  .charts-col {
    padding: 4px 4px 4px 2px !important;
  }
  .time-series {
    padding: 4px !important;
  }
</style>
