<template>
  <b-navbar toggleable="lg" type="dark" variant="info" sticky>
    <b-navbar-brand to="/">SocialTrails</b-navbar-brand>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav>
        <b-nav-text>Monitoring Recreation with Social Media</b-nav-text>
      </b-navbar-nav>
      <b-navbar-nav class="ml-auto">
        <b-nav-form v-on:submit="doNothing" v-show="this.$store.getters.getSelectedProjectCode">
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
      }
    }
  }
</script>

<style scoped>
  .form-input {
    margin: 0 10px 0 10px;
  }
</style>
