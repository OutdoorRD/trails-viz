<template>
  <b-navbar toggleable="lg" type="dark" variant="info" sticky>
    <b-navbar-brand href="https://outdoorrd.org/"   target="_blank">
      <img :src="logo" alt="Outdoor R&D Logo" class="navbar-logo" />
    </b-navbar-brand>
    <b-navbar-brand to="/">TrailTrends</b-navbar-brand>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav>
        <b-nav-text>Mapping outdoor recreation on public lands</b-nav-text>
      </b-navbar-nav>
      <b-navbar-nav class="ml-auto">
        <b-nav-form v-on:submit="doNothing">
          <b-form-input
            class="form-input"
            size="sm"
            list="project-sites-list"
            placeholder="Search Trail"
            v-model="siteSearchText"
            v-on:keyup="autoCompleteSite"
            v-on:change="emitSiteNameEvent"
            v-show="this.$store.getters.getSelectedProjectCode"
          ></b-form-input>
          <b-form-datalist
            id="project-sites-list"
            :options="filteredSites"
          ></b-form-datalist>

          <b-button
            size="sm"
            class="my-2 my-sm-0"
            variant="login-color"
            to="/login"
            v-show="this.$store.getters.getLoggedInUser === 'anon'"
            >Login</b-button
          >

          <b-nav-item-dropdown
            v-bind:text="this.$store.getters.getLoggedInUser"
            v-show="this.$store.getters.getLoggedInUser !== 'anon'"
            right
          >
            <b-dropdown-item v-on:click="gotoUserProfile"
              >Profile</b-dropdown-item
            >
            <b-dropdown-item
              v-if="this.$store.getters.getUserRole === 'admin'"
              v-on:click="gotoAdministration"
              >Administration</b-dropdown-item
            >

            <b-dropdown-item v-on:click="logout">Logout</b-dropdown-item>
          </b-nav-item-dropdown>
        </b-nav-form>
      </b-navbar-nav>
    </b-collapse>
  </b-navbar>
</template>

<script>
import { EventBus } from "../event-bus";
import { Cookie } from "../cookie";
import logo from "../assets/ORandD_Logo_white.png";


export default {
  name: "TopBar",
  data: function() {
    return {
      logo,
      siteSearchText: "",
      filteredSites: [],
    };
  },
  methods: {
    autoCompleteSite: function() {
      const projectSites = Object.values(this.$store.getters.getProjectSites);
      const trailNames = projectSites.map((site) => site.trailName);
      if (
        this.siteSearchText.startsWith("#") &&
        this.siteSearchText.length >= 2
      ) {
        const siteIdSearchText = this.siteSearchText.substring(1).toUpperCase();
        this.filteredSites = projectSites
          .filter((site) => site.siteid.startsWith(siteIdSearchText))
          .map((site) => site.trailName);
      } else if (this.siteSearchText.length >= 2) {
        this.filteredSites = trailNames.filter((name) =>
          name.toUpperCase().includes(this.siteSearchText.toUpperCase())
        );
      } else {
        this.filteredSites = [];
      }
      EventBus.$emit("top-bar:site-search-results", this.filteredSites);
    },
    emitSiteNameEvent: function() {
      const projectSites = Object.values(this.$store.getters.getProjectSites);
      let selectedSite = undefined;
      if (this.siteSearchText.startsWith("#")) {
        selectedSite = projectSites.find(
          (site) =>
            site.siteid === this.siteSearchText.substring(1).toUpperCase()
        );
      } else {
        selectedSite = projectSites.find(
          (site) => site.trailName === this.siteSearchText
        );
      }
      if (selectedSite) {
        EventBus.$emit("top-bar:site-selected", selectedSite); // Emit the site object
      }
      EventBus.$emit("top-bar:site-search-results", []);
      this.filteredSites = [];
      this.siteSearchText = "";
    },
    doNothing: function(event) {
      event.preventDefault();
    },
    gotoUserProfile: function() {
      let username = this.$store.getters.getLoggedInUser;
      this.$router.push({ name: "user", params: { username: username } });
    },
    gotoAdministration: function() {
      this.$router.push({ path: "/administration" });
    },
    logout: function() {
      this.$store.dispatch("setLoggedInUser", "anon");
      Cookie.delete("username");
      Cookie.delete("authHeader");
      Cookie.delete("userRole");

      if (this.$route.path !== "/") {
        this.$router.push({ path: "/" });
      }
    },
  },
};
</script>

<style scoped>

.form-input {
  margin: 0 10px 0 10px;
}

.navbar-logo {
  max-height: 80px;      
}

.navbar.bg-info {
  background-color: var(--color-primary) !important;
  height: 80px
}

.navbar {
  font-family: 'Roboto Condensed', sans-serif;
}

.navbar-brand {
  font-size: 1.4rem !important; /* ~24px if base is 16px */
  letter-spacing: 0.02em !important;
}
/* .navbar-text  {
  color: var(--color-tertiary) !important; 
} */
.btn-login-color {
  background-color: #fff;  /* Bootstrap purple */
  border-color:     #1f78b4;
  color:            #1f78b4;
}
.btn-login-color:hover {
  background-color: #a6cee3;  /* a tad darker for hover */
  border-color:     #a6cee3;
  color:            #000;
}


</style>
