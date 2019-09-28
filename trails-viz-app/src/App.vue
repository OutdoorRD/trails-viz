<template>
  <b-container fluid id="app">
    <top-bar v-on:project-selected="sendProjectSelectedEventToMap" v-on:site-selected="sendSiteSelectedEventToMap"></top-bar>
    <b-row no-gutters>
      <b-col sm="8" class="map-col">
        <map-div ref="map-div" id="mapDiv" v-on:site-selected="sendSiteSelectedToBarGraph"></map-div>
      </b-col>
      <b-col sm="4" class="graph-col">
        <bar-graph ref="bar-graph"></bar-graph>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import MapDiv from "@/components/MapDiv";
import TopBar from "@/components/TopBar";
import BarGraph from "@/components/BarGraph";

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
    sendSiteSelectedToBarGraph: function () {
      this.$refs['bar-graph'].renderBarGraph();
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
