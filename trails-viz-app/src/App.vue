<template>
  <b-container fluid id="app">
    <top-bar class="top-bar"></top-bar>
    <router-view></router-view>
  </b-container>
</template>

<script>
import TopBar from "./components/TopBar";

import axios from "axios";
import {Cookie} from "./cookie";

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

    // Check cookies if user is logged in
    let userName = Cookie.get('userName');
    if (userName !== undefined) {
      self.$store.dispatch('setLoggedInUser', userName);
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
