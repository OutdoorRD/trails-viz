<template>
  <b-container fluid id="app">
    <top-bar v-on:project-selected="sendEventToMap"></top-bar>
    <b-row no-gutters>
      <b-col sm="8">
        <map-div ref="map-div" id="mapDiv" v-on:site-selected="sendSiteSelectedToBarGraph"></map-div>
      </b-col>
      <b-col sm="4">
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
    sendEventToMap: function (selectedProject) {
      this.$refs['map-div'].renderProjectSites(selectedProject)
    },
    sendSiteSelectedToBarGraph: function (selectedSite) {
      this.$refs['bar-graph'].renderBarGraph(selectedSite);
    }
  }
}
</script>

<style>
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    padding: 0;
  }
</style>
