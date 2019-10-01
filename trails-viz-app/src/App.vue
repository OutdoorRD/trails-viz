<template>
  <b-container fluid id="app">
    <top-bar v-on:project-selected="sendProjectSelectedEventToMap" v-on:site-selected="sendSiteSelectedEventToMap"></top-bar>
    <b-row no-gutters>
      <b-col sm="7" class="map-col">
        <map-div ref="map-div" id="mapDiv" v-on:site-selected="sendRenderPlotEvents"></map-div>
      </b-col>
      <b-col sm="5" class="graph-col">
        <bar-graph ref="bar-graph"></bar-graph>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import MapDiv from "@/components/MapDiv";
import TopBar from "@/components/TopBar";
import BarGraph from "@/components/BarGraph";
import {store} from "./store";
import axios from "axios";

export default {
  name: 'app',
  components: {
    BarGraph,
    TopBar,
    MapDiv
  },
  methods: {
    sendProjectSelectedEventToMap: function () {
      this.$refs['map-div'].renderProjectSites()
    },
    sendSiteSelectedEventToMap: function(trailName) {
      this.$refs['map-div'].selectSite(trailName)
    },
    sendRenderPlotEvents: function () {
      // populate the estimates in global store to be used in bar graph and time series
      let siteid = store.selectedSite['siteid'];
      axios.all([
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/annualEstimates'),
        axios.get(this.$apiEndpoint + '/sites/' + siteid + '/monthlyEstimates')
      ]).then(axios.spread((annualResponse, monthlyResponse) => {
        store.setAnnualEstimates(annualResponse.data);
        store.setMonthlyEstimates(monthlyResponse.data);
        this.$refs['bar-graph'].renderDefaultGraph();
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
  .graph-col {
    padding: 4px 4px 4px 2px !important;
  }
</style>
