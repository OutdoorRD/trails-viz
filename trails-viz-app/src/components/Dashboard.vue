<template>
  <!-- <div> -->
    <!-- <b-alert
      :show="dismissCountDown"
      dismissible
      fade
      variant="warning"
      @dismiss-count-down="countDownChanged"
      class="mb-0"
    >
      For full access to Visitor Characteristics and data downloads, please email <a href="mailto:outdoorrd@uw.edu">outdoorrd@uw.edu</a>.
    </b-alert> -->
  <b-row no-gutters class="app-container">
    <b-col sm="6" class="map-col">
      <map-div
        ref="map-div"
        id="mapDiv"
      ></map-div>
    </b-col>
    <b-col sm="6" class="charts-col">
      <b-row no-gutters>
        <b-col sm="7">
          <b-breadcrumb
            :items="breadcrumbItems"
            class="app-breadcrumb"
          ></b-breadcrumb>
        </b-col>
        <b-col sm="5">
          <b-button-group class="app-button-group d-flex">
            <b-button
              v-on:click="showSelectedTab('visitation')"
              class="app-button"
              v-bind:class="{ active: visibleTabGroup === 'visitation' }"
              >Visitation</b-button
            >
            <b-button
              v-if="availableDataSources.length > 0"
              v-on:click="showSelectedTab('visitorCharacteristics')"
              class="app-button"
              v-bind:class="{
                active: visibleTabGroup === 'visitorCharacteristics',
              }"
              :disabled="this.$store.getters.getVizMode === 'compare'"
              v-show="this.$store.getters.getLoggedInUser !== 'anon'"
              >Visitor Characteristics</b-button
            >
          </b-button-group>
        </b-col>
      </b-row>
      <!-- Radio Button Row -->
      <b-form inline class="mb-2" v-if="visibleTabGroup === 'visitorCharacteristics' && availableDataSources.length">
        <label class="mr-2 font-weight-bold">Select Data Source:</label>
        <b-form-radio-group v-model="selectedSource" buttons button-variant="outline-primary" size="sm">
          <b-form-radio 
            v-for="source in availableDataSources" 
            :key="source" 
            :value="source.split(' ')[0].toLowerCase()"
            :disabled="activeSubTab === 'Party Characteristics' && !source.toLowerCase().includes('chatbot')">
            {{ source }}
          </b-form-radio>
        </b-form-radio-group>
      </b-form>
      <b-row no-gutters>
        <b-col sm="12">
          <info-viewer
            ref="project-info"
            v-show="visibleTabGroup === 'project-info'"
          ></info-viewer>
          <b-tabs v-show="visibleTabGroup === 'visitation'">
            <b-tab title="Time Series">
              <time-series ref="time-series"></time-series>
            </b-tab>
            <b-tab title="Bar Graph">
              <bar-graph ref="bar-graph"></bar-graph>
            </b-tab>
            <b-tab title="Methods">
              <info-viewer ref="visitation-info"></info-viewer>
            </b-tab>
          </b-tabs>

          <b-tabs v-show="visibleTabGroup === 'visitorCharacteristics'" class="tab-group">
            <b-tab
              title="Home Locations"
              @click="handleSubTabClick('Home Locations')"
            >
              <home-locations ref="home-locations"></home-locations>
            </b-tab>
            <b-tab
              title="Home Locations Map"
              v-on:update:active="activateHomeLocationsMap"
              @click="handleSubTabClick('Home Locations Map')"
            >
              <home-locations-map ref="home-locations-map"></home-locations-map>
            </b-tab>
            <b-tab
              title="Demographics"
              @click="handleSubTabClick('Demographics')"
            >
              <demographics-summary
                ref="demographics-summary"
              ></demographics-summary>
            </b-tab>
            <b-tab
              title="Party Characteristics"
              @click="handleSubTabClick('Party Characteristics')"
              v-if="availableDataSources.some(source => source.toLowerCase().includes('chatbot'))"
            >
              <party-characteristics ref="party-characteristics"></party-characteristics>
            </b-tab>
            <b-tab title="Methods" @click="handleSubTabClick('Methods')">
              <info-viewer ref="home-locations-info"></info-viewer>
            </b-tab>
          </b-tabs>
        </b-col>
      </b-row>
    </b-col>
  </b-row>
  <!-- </div> -->

</template>

<script>
import axios from "axios";

import MapDiv from "../components/MapDiv";
import BarGraph from "../components/BarGraph";
import TimeSeries from "../components/TimeSeries";
import HomeLocations from "../components/HomeLocations";
import HomeLocationsMap from "../components/HomeLocationsMap";
import InfoViewer from "../components/InfoViewer";
import DemographicsSummary from "../components/DemographicsSummary";
import PartyCharacteristics from "../components/PartyCharacteristics";

import { VIZ_MODES, DATA_SOURCES } from "../store/constants";
import { EventBus } from "../event-bus";

export default {
  name: "Dashboard",
  data: function() {
    return {
      dismissSecs: 30,
      breadcrumbItems: [],
      // dismissCountDown: 0,
      trailName: "",
      comparingTrailName: "",
      activeSubTab: "",
    };
  },
  computed: {
    visibleTabGroup: {
      get() {
        return this.$store.getters.getVisibleTabGroup;
      },
      set(newTab) {
        this.$store.dispatch('setVisibleTabGroup', newTab);
      }
    },
    availableDataSources() {
      const projectCode = this.$route.params.project;
      return DATA_SOURCES[this.$store.getters.getProjectCodeToName[projectCode]] || [];
    },
    selectedSource: {
      get() {
        return this.$store.getters.getSelectedSource;
      },
      set(value) {
        this.$store.dispatch('setSelectedSource', value);
      }
    }
  },
  mounted() {
    // This part of code has been duplicated from App
    // because in case of hitting the project URL directly
    // app won't load in time to have these global variables populated
    // this.showAlert();
    this.$store.dispatch('setVisibleTabGroup', 'project-info');
    this.$store.dispatch('setSelectedSource', '');
    if (!this.$store.getters.getSelectedSource && this.availableDataSources.length > 0) {
      const initialSource = this.availableDataSources[0].split(" ")[0].toLowerCase();
      this.$store.dispatch('setSelectedSource', initialSource);
    }
    let self = this;
    if (Object.keys(self.$store.getters.getAllProjects).length === 0) {
      axios.get(self.$apiEndpoint + "/projects").then((response) => {
        let allProjects = response.data;
        let projectCodeToName = {};
        for (let [name, code] of Object.entries(allProjects)) {
          projectCodeToName[code] = name;
        }
        self.$store.dispatch("setAllProjects", allProjects);
        self.$store.dispatch("setProjectCodeToName", projectCodeToName);

        this.renderProjectLevelPlots();
        if (!this.selectedSource || this.selectedSource === "") {
          this.selectedSource = this.availableDataSources.length > 0
            ? this.availableDataSources[0].split(" ")[0].toLowerCase()
            : "";
        }
      });
    } else {
      this.renderProjectLevelPlots();
    }

    EventBus.$on("map-div:site-selected", self.renderSiteLevelPlots);
    EventBus.$on("map-div:compare-activated", self.renderComparisionPlots);
  },
  beforeDestroy() {
    let self = this;
    EventBus.$off("map-div:site-selected", self.renderSiteLevelPlots);
    EventBus.$off("map-div:compare-activated", self.renderComparisionPlots);
  },
  components: {
    InfoViewer,
    DemographicsSummary,
    PartyCharacteristics,
    HomeLocationsMap,
    HomeLocations,
    TimeSeries,
    BarGraph,
    MapDiv,
  },
  methods: {
    renderProjectLevelPlots: function() {
      this.$store.dispatch("setVizMode", VIZ_MODES.PROJECT);

      let projectCode = this.$route.params.project;
      let projectName = this.$store.getters.getProjectCodeToName[projectCode];
      this.$store.dispatch("setSelectedProjectCode", projectCode);
      this.$store.dispatch("setSelectedProjectName", projectName);

      this.breadcrumbItems.push({
        text: projectName,
        href: "/dashboard/" + projectCode,
      });

      this.trailName = "All Sites in " + projectName;
      this.$store.dispatch("setSelectedSite", {
        trailName: projectName,
        setStyle: (x) => x,
      }); // a dummy set style method which does nothing

      // before rendering plots, call the API to get data sources and
      // set to global store
      let self = this;
      axios
        .get(self.$apiEndpoint + "/projects/" + projectCode + "/dataSources")
        .then((response) => {
          self.$store.dispatch("setSelectedProjectDataSources", response.data);

          self.$refs["map-div"].renderProjectSites();

          // render plots on project level
          self.$refs["bar-graph"].renderDefaultGraph();
          self.$refs["time-series"].renderTimeSeries();
          self.$refs["home-locations"].renderTreeMap();
          self.$refs["home-locations-map"].renderHomeLocationsMap();
          self.$refs["project-info"].renderInfo("project");
          self.$refs["visitation-info"].renderInfo("visitation");
          self.$refs["home-locations-info"].renderInfo("homeLocations");
          self.$refs["demographics-summary"].renderDemographicsSummary();
          self.$refs["party-characteristics"].renderPartyCharacteristics();
        });
    },
    renderSiteLevelPlots: function() {
      this.trailName = this.$store.getters.getSelectedSite["trailName"];
      this.comparingTrailName = "";

      if (this.breadcrumbItems.length > 1) {
        this.breadcrumbItems.pop();
      }
      this.breadcrumbItems.push({
        text: this.trailName,
        href: "javascript:void()",
      });

      this.$store.dispatch("setVizMode", VIZ_MODES.SITE);
      this.$refs["bar-graph"].renderDefaultGraph();
      this.$refs["time-series"].renderTimeSeries();
      this.$refs["home-locations"].renderTreeMap();
      this.$refs["home-locations-map"].renderHomeLocationsMap();
      this.$refs["demographics-summary"].renderDemographicsSummary();
      this.$refs["party-characteristics"].renderPartyCharacteristics();
    },
    renderComparisionPlots: function() {
      this.$store.dispatch("setVizMode", VIZ_MODES.COMPARE);
      this.comparingTrailName = this.$store.getters.getComparingSite[
        "trailName"
      ];

      // hide the visitor characteristics tab group when comparing
      this.visibleTabGroup = "visitation";

      if (this.breadcrumbItems.length > 1) {
        this.breadcrumbItems.pop();
      }
      this.breadcrumbItems.push({
        text: this.trailName + " vs " + this.comparingTrailName,
        href: "javascript:void()",
      });

      this.$refs["bar-graph"].renderDefaultGraph();
      this.$refs["time-series"].renderTimeSeries();
    },
    showSelectedTab: function(tab) {
      this.visibleTabGroup = tab;
    },
    handleSubTabClick(subTabName) {
      this.activeSubTab = subTabName;
      if (subTabName === 'Party Characteristics') {
        this.selectedSource = 'chatbot';
      }
    },
    activateHomeLocationsMap: function(event) {
      // The event here is a boolean variable which tell if the
      // tab was activated (true) or deactivated (false)
      if (event) {
        this.$refs["home-locations-map"].activateHomeLocationsMap();
      }
    },
    // countDownChanged(dismissCountDown) {
    //   this.dismissCountDown = dismissCountDown;
    // },
    // showAlert() {
    //   if (this.$store.getters.getLoggedInUser === 'anon') {
    //     this.dismissCountDown = this.dismissSecs;
    //   }
    // },
  },
};
</script>

<style scoped>
.app-container {
  height: calc(100vh - 60px);
}

.map-col {
  padding: 4px 4px 4px 4px !important;
}

.charts-col {
  padding: 4px 4px 4px 4px !important;
}

.app-breadcrumb {
  height: 38px;
  padding: 8px 8px 8px 8px;
}

.app-button-group {
  margin-left: 8px;
}

.app-button {
  color: #6c757d;
  background-color: #e9ecef;
}

.tab-group {
  font-size: 0.95rem;
}
</style>
