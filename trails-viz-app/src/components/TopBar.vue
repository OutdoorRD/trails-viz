<template>
  <div>
    <b-navbar toggleable="lg" type="dark" variant="info">
      <b-navbar-brand>SocialTrails</b-navbar-brand>

      <b-nav-text>Monitoring Recreation with Social Media</b-nav-text>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">
        <b-form-input size="sm" list="project-list" placeholder="Type Project Name" v-model="searchText" v-on:keyup="autoComplete" v-on:change="emitEvent"></b-form-input>
        <b-form-datalist id="project-list" :options="filteredProjects"></b-form-datalist>
      </b-navbar-nav>

    </b-navbar>
  </div>
</template>

<script>
  import axios from 'axios';

  export default {
    name: "TopBar",
    mounted: function() {
      let self = this;
      axios.get(self.$apiEndpoint + "/projects")
        .then(response => self.allProjects = response.data)
    },
    data: function () {
      return {
        allProjects: [],
        filteredProjects: [],
        searchText: ''
      };
    },
    methods: {
      autoComplete: function () {
        if (this.allProjects.includes(this.searchText.toUpperCase())) {
          // don't show suggestions when a valid project is selected
          return
        }
        if (this.searchText.length >= 1) {
          this.filteredProjects = this.allProjects.filter(name => name.toUpperCase().includes(this.searchText.toUpperCase()));
        } else {
          this.filteredProjects = []
        }
      },
      emitEvent: function () {
        if (this.filteredProjects.includes(this.searchText.toUpperCase())) {
          this.$emit('project-selected', this.searchText.toUpperCase())
        }
      }
    }
  }
</script>

<style scoped>

</style>
