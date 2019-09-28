<template>
  <b-navbar toggleable="lg" type="dark" variant="info">
    <b-navbar-brand>SocialTrails</b-navbar-brand>

    <b-nav-text>Monitoring Recreation with Social Media</b-nav-text>

    <!-- Right aligned nav items -->
    <b-navbar-nav class="ml-auto">
      <b-nav-form v-on:submit="doNothing">
        <b-form-input size="sm" list="project-list" placeholder="Search Project" v-model="projectSearchText" v-on:keyup="autoCompleteProject" v-on:change="emitProjectNameEvent"></b-form-input>
        <b-form-datalist id="project-list" :options="filteredProjects"></b-form-datalist>
      </b-nav-form>
    </b-navbar-nav>
  </b-navbar>
</template>

<script>

  import {store} from '../store'

  export default {
    name: "TopBar",
    mounted: function() {
      store.fetchAllProjects()
    },
    data: function () {
      return {
        projectSearchText: '',
        filteredProjects: [],
        siteSearchText: '',
        filteredSites: []
      };
    },
    methods: {
      autoCompleteProject: function () {
        if (store.allProjects.includes(this.projectSearchText.toUpperCase())) {
          // don't show suggestions when a valid project is selected
          return
        }
        if (this.projectSearchText.length >= 1) {
          this.filteredProjects = store.allProjects.filter(name => name.toUpperCase().includes(this.projectSearchText.toUpperCase()));
        } else {
          this.filteredProjects = []
        }
      },
      emitProjectNameEvent: function () {
        if (this.filteredProjects.includes(this.projectSearchText.toUpperCase())) {
          store.setSelectedProject(this.projectSearchText.toUpperCase());
          this.$emit('project-selected');
        }
      },
      doNothing: function(event) {
        event.preventDefault()
      }
    }
  }
</script>

<style scoped>

</style>
