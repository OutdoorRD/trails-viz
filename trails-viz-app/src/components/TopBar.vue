<template>
  <b-navbar toggleable="lg" type="dark" variant="info" sticky>
    <b-navbar-brand to="/">SocialTrails</b-navbar-brand>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav>
        <b-nav-text>Monitoring Recreation with Social Media</b-nav-text>
      </b-navbar-nav>
      <b-navbar-nav class="ml-auto">
        <b-nav-form v-on:submit="doNothing">
          <b-form-input class="form-input" size="sm" list="project-sites-list" placeholder="Search Trail"
                        v-model="siteSearchText" v-on:keyup="autoCompleteSite" v-on:change="emitSiteNameEvent"
                        v-show="this.$store.getters.getSelectedProjectCode"></b-form-input>
          <b-form-datalist id="project-sites-list" :options="filteredSites"></b-form-datalist>

          <b-button size="sm" class="my-2 my-sm-0" variant="info" to="/login"
                    v-show="this.$store.getters.getLoggedInUser === 'anon'">Login</b-button>

          <b-nav-item-dropdown v-bind:text="this.$store.getters.getLoggedInUser"
                               v-show="this.$store.getters.getLoggedInUser !== 'anon'" right>
            <b-dropdown-item v-on:click="gotoUserProfile">Profile</b-dropdown-item>
            <b-dropdown-item v-on:click="logout">Logout</b-dropdown-item>
          </b-nav-item-dropdown>

        </b-nav-form>
      </b-navbar-nav>
    </b-collapse>

  </b-navbar>
</template>

<script>

  import {EventBus} from '../event-bus'

  export default {
    name: "TopBar",
    data: function () {
      return {
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
        EventBus.$emit('top-bar:site-selected', this.siteSearchText);
        this.siteSearchText = '';
      },
      doNothing: function(event) {
        event.preventDefault()
      },
      gotoUserProfile: function () {
        let userName = this.$store.getters.getLoggedInUser;
        this.$router.push({name: 'user', params: {userName: userName}});
      },
      logout: function () {
        this.$store.dispatch('setLoggedInUser', 'anon');
        this.$router.push('/')
      }
    }
  }
</script>

<style scoped>
  .form-input {
    margin: 0 10px 0 10px;
  }
</style>
