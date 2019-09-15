<template>
  <div id="app">
    <map-div></map-div>
  </div>
</template>

<script>
import MapDiv from "@/components/MapDiv";

export default {
  name: 'app',
  components: {
    MapDiv
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
