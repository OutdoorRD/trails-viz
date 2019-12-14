<template>
  <b-container fluid id="app">
    <top-bar v-on:site-selected="sendSiteSelectedEventToMap" class="top-bar"></top-bar>
    <vue-page-transition>
      <router-view></router-view>
    </vue-page-transition>
  </b-container>
</template>

<script>
import TopBar from "./components/TopBar";

import axios from "axios";

export default {
  name: 'app',
  components: {
    TopBar
  },
  mounted() {
    let self = this;
    axios.get(self.$apiEndpoint + '/projects')
      .then(response => {
        let allProjects = response.data;
        let projectCodeToName = {};
        for (let [name, code] of Object.entries(allProjects)) {
          projectCodeToName[code] = name
        }
        self.$store.dispatch('setAllProjects', allProjects);
        self.$store.dispatch('setProjectCodeToName', projectCodeToName);
      });
  },
  methods: {
    sendSiteSelectedEventToMap: function(trailName) {
      this.$refs['map-div'].selectSite(trailName)
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
</style>
