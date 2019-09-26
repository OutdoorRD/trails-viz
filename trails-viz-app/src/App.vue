<template>
  <b-container fluid id="app">
    <top-bar v-on:project-selected="sendEventToMap"></top-bar>
    <b-row no-gutters>
      <b-col sm="8" class="show-border">
        <map-div ref="map-div" id="mapDiv"></map-div>
      </b-col>
      <b-col sm="4" class="show-border">
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
