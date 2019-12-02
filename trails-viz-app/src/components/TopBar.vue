<template>
  <b-navbar toggleable="lg" type="dark" variant="info" sticky>
    <b-navbar-brand href="javascript:void()" v-on:click="moveToTop">SocialTrails</b-navbar-brand>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav>
        <b-nav-text>Monitoring Recreation with Social Media</b-nav-text>
      </b-navbar-nav>
      <b-navbar-nav class="ml-auto">
        <b-nav-form v-on:submit="doNothing" v-show="this.$store.getters.getSelectedProjectCode">
          <b-form-input class="form-input" size="sm" list="project-list" placeholder="Search Project" v-model="projectSearchText" v-on:keyup="autoCompleteProject" v-on:change="emitProjectNameEvent"></b-form-input>
          <b-form-datalist id="project-list" :options="filteredProjects"></b-form-datalist>

          <b-form-input class="form-input" size="sm" list="project-sites-list" placeholder="Search Trail" v-model="siteSearchText" v-on:keyup="autoCompleteSite" v-on:change="emitSiteNameEvent"></b-form-input>
          <b-form-datalist id="project-sites-list" :options="filteredSites"></b-form-datalist>
        </b-nav-form>
      </b-navbar-nav>
    </b-collapse>

  </b-navbar>
</template>

<script>

  export default {
    name: "TopBar",
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
        let allProjects = this.$store.getters.getAllProjects;
        let projectNames = Object.keys(allProjects);
        let projectNamesUpperCase = projectNames.map(name => name.toUpperCase());

        if (projectNamesUpperCase.includes(this.projectSearchText.toUpperCase())) {
          // don't show suggestions when a valid project is selected
          return
        }
        if (this.projectSearchText.length >= 1) {
          this.filteredProjects = projectNames.filter(name => name.toUpperCase().includes(this.projectSearchText.toUpperCase()));
        } else {
          this.filteredProjects = []
        }
      },
      emitProjectNameEvent: function () {
        if (this.filteredProjects.includes(this.projectSearchText)) {
          this.$store.dispatch('clearSelectedProjectData');
          this.$store.dispatch('setSelectedProjectName', this.projectSearchText);
          this.$store.dispatch('setSelectedProjectCode', this.$store.getters.getAllProjects[this.projectSearchText]);
          this.$emit('project-selected');
          this.projectSearchText = '';
        }
      },
      autoCompleteSite:  function() {
        let trailNames = Object.keys(this.$store.getters.getProjectSites);

        if (trailNames.includes(this.siteSearchText)) {
          return
        }
        if (this.siteSearchText.length >= 2) {
          this.filteredSites = trailNames.filter(name => name.toUpperCase().includes(this.siteSearchText.toUpperCase()));
        } else {
          this.filteredSites = []
        }
      },
      emitSiteNameEvent: function() {
        this.$emit('site-selected', this.siteSearchText);
        this.siteSearchText = '';
      },
      doNothing: function(event) {
        event.preventDefault()
      },
      moveToTop: function () {
        document.getElementById("landing-page").scrollIntoView({behavior: "smooth", block: "end"})
      }
    }
  }
</script>

<style scoped>
  .form-input {
    margin: 0 10px 0 10px;
  }
</style>
