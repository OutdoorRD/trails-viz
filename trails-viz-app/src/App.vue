<template>
  <b-container fluid id="app">
    <top-bar></top-bar>
    <map-div></map-div>
  </b-container>
</template>

<script>
import MapDiv from "@/components/MapDiv";
import TopBar from "@/components/TopBar";

export default {
  name: 'app',
  components: {
    TopBar,
    MapDiv
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
