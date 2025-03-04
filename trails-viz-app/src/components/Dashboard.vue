<template>
  <b-row no-gutters class="app-container">
    <b-col sm="6" class="map-col">
      <map-div
        ref="map-div"
        id="mapDiv"
        :visible-tab-group="visibleTabGroup"
        :selected-source="selectedSource"
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
      <b-form inline class="mb-2" v-if="visibleTabGroup === 'visitorCharacteristics'">
        <label class="mr-2 font-weight-bold">Select Data Source:</label>
        <b-form-radio-group v-model="selectedSource" buttons button-variant="outline-primary" size="sm">
          <b-form-radio value="chatbot">Chatbot (2018 - 2024)</b-form-radio>
          <b-form-radio value="flickr" :disabled="activeSubTab === 'Party Characteristics'">
            Flickr (2005 - 2019)
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
              <home-locations ref="home-locations" :selected-source="selectedSource"></home-locations>
            </b-tab>
            <b-tab
              title="Home Locations Map"
              v-on:update:active="activateHomeLocationsMap"
              @click="handleSubTabClick('Home Locations Map')"
            >
              <home-locations-map ref="home-locations-map" :selected-source="selectedSource"></home-locations-map>
            </b-tab>
            <b-tab
              title="Demographics"
              @click="handleSubTabClick('Demographics')"
            >
              <demographics-summary
                ref="demographics-summary"
                :selected-source="selectedSource"
              ></demographics-summary>
            </b-tab>
            <b-tab
              title="Party Characteristics"
              @click="handleSubTabClick('Party Characteristics')"
            >
              <party-characteristics
                ref="party-characteristics"
              ></party-characteristics>
            </b-tab>
            <b-tab title="Methods" @click="handleSubTabClick('Methods')">
              <info-viewer ref="home-locations-info"></info-viewer>
            </b-tab>
          </b-tabs>
        </b-col>
      </b-row>
    </b-col>
  </b-row>
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

import { VIZ_MODES } from "../store/constants";
import { EventBus } from "../event-bus";

export default {
  name: "Dashboard",
  data: function() {
    return {
      breadcrumbItems: [],
      trailName: "",
      comparingTrailName: "",
      visibleTabGroup: "project-info",
      activeSubTab: "",
      selectedSource: "chatbot",
    };
  },
  mounted() {
    // This part of code has been duplicated from App
    // because in case of hitting the project URL directly
    // app won't load in time to have these global variables populated
    let self = this;
    if (self.$store.getters.getAllProjects === undefined) {
      axios.get(self.$apiEndpoint + "/projects").then((response) => {
        let allProjects = response.data;
        let projectCodeToName = {};
        for (let [name, code] of Object.entries(allProjects)) {
          projectCodeToName[code] = name;
        }
        self.$store.dispatch("setAllProjects", allProjects);
        self.$store.dispatch("setProjectCodeToName", projectCodeToName);

        this.renderProjectLevelPlots();
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
    handleSelectedSource(selectedSource) {
      this.selectedSource = selectedSource
    },
    activateHomeLocationsMap: function(event) {
      // The event here is a boolean variable which tell if the
      // tab was activated (true) or deactivated (false)
      if (event) {
        this.$refs["home-locations-map"].activateHomeLocationsMap();
      }
    },
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
