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
    <b-row no-gutters>
      <b-col sm="12" class="time-series">
        <time-series ref="time-series"></time-series>
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
import TimeSeries from "@/components/TimeSeries";

export default {
  name: 'app',
  components: {
    TimeSeries,
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
  .time-series {
    padding: 4px !important;
  }
</style>
