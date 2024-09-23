<template>
  <b-container fluid id="app">
    <top-bar class="top-bar"></top-bar>
    <router-view></router-view>
    <div>
      <b-modal id="unauthorizedModal" ref="unauthorizedModal" title="Unauthorized" centered ok-only
               header-bg-variant="secondary" header-text-variant="light" ok-variant="danger">
        <p>Your are not authorized to access this project!</p>
      </b-modal>
    </div>
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
    // leaving a comment to test out frontend CI/CD
    // add interceptor to show modal when 403 response is received
    axios.interceptors.response.use(
      response => response,
      error => {
        if (403 === error.response.status) {
          let modal = self.$refs['unauthorizedModal'];
          if (!modal.visible) {
            self.$bvModal.show('unauthorizedModal');
          }
        }
        return Promise.reject(error);
      }
    );

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
