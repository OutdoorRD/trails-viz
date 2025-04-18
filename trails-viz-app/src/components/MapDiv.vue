<template>
  <div class="map-root">
    <b-alert
      :show="dismissCountDown"
      dismissible
      fade
      variant="warning"
      @dismiss-count-down="countDownChanged"
    >
      Only two sites can be compared at a time!
    </b-alert>
    <!-- Range Slider for Year Selection -->

      <div v-if="showChatbotMapCondition" class="range-slider-container">
        <v-card
          style="
        max-width: 100%;
        padding: 10px;
        margin: 0; 
        display: flex;
        flex-direction: column;
        align-items: center; 
        justify-content: flex-start;
        background-color: white;
        border-radius: 4px;
      "
        >
          <label
            for="year-range-slider"
            style="
          font-size: 14px;
          display: block;
          font-weight: bold;
          text-align: center; 
          width: 100%;
          font-family: 'Helvetica Neue', Arial, Helvetica, sans-serif;
          color: #333;
          margin:0;
        "
          >
            Year Range
          </label>
          <v-range-slider
            id="year-range-slider"
            v-if="yearRange && minYear !== undefined && maxYear !== undefined"
            v-model="tempYearRange"
            :min="minYear"
            :max="maxYear"
            ticks="always"
            tick-size="4"
            thumb-label
            hide-details
            @end="onYearRangeChange"
            style="
            width: 100%;
            margin: 0;
            padding: 0;
            "
          >
            <template v-slot:prepend>
              <span>{{ minYear }}</span>
            </template>
            <template v-slot:append>
              <span>{{ maxYear }}</span>
            </template>
          </v-range-slider>
        </v-card>
      </div>

      <div class="map-container">
        <div class="map-div" ref="mapDiv"></div>
        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner"></div>
          <p class="loading-text">Loading data...</p>
        </div>
      </div>
  </div>
</template>

<script>
import L from "leaflet";
import axios from "axios";
import { MAPBOX_CONSTS } from "../store/constants";
import { EventBus } from "../event-bus";
import * as turf from "@turf/turf";
// import '../assets/styles/layout.css';
// The following two statements are required because of an issue with leaflet and webpack
// see https://github.com/Leaflet/Leaflet/issues/4968#issuecomment-483402699
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

// Make the fault marker of leaflet smaller
L.Icon.Default.prototype.options.iconAnchor = [6, 20];
L.Icon.Default.prototype.options.iconSize = [13, 20];
L.Icon.Default.prototype.options.shadowSize = [20, 20];

// Update icon URL to use the SVG
// let IconSuper = L.Icon.extend({
//   options: L.Icon.Default.prototype.options,
// });

const defaultStyle = {
  color: "#C04000",
  weight: 1,
  fillColor: "#C04000",
  fillOpacity: 0.2,
};

const solidDefaultStyle = {
  color: "#EC5800",
  weight: 1,
  fillColor: "#EC5800",
  fillOpacity: 0.2,
};

const solidGreyStyle = {
  color: "#545454",
  weight: 1,
  fillColor: "#545454",
  fillOpacity: 0.2,
};

const hoverStyle = {
  color: "#ffb801",
  weight: 1,
  fillColor: "#ffb801",
  fillOpacity: 0.2,
};

const selectedStyle = {
  color: "#0000ff",
  weight: 1,
  fillColor: "#0000ff",
  fillOpacity: 0.2,
};

const compareStyle = {
  color: "#fa00ff",
  weight: 1,
  fillColor: "#fa00ff",
  fillOpacity: 0.8,
};

const bubbleDefaultStyle = {
  color: "#C04000",
  weight: 1,
  fillColor: "#C04000",
  fillOpacity: 0.2,
};

const highlightStyle = {
  color: "#8A00C4",
  weight: 1,
  fillColor: "#8A00C4",
  fillOpacity: 0.4,
};

const bubbleHighlightStyle = {
  color: "#8A00C4",
  weight: 1,
  fillColor: "#8A00C4",
  fillOpacity: 0.4,
};

export default {
  name: "MapDiv",
  data: function() {
    return {
      dismissSecs: 5,
      dismissCountDown: 0,
      sitesLayer: [],
      bubblesLayer: [],
      chatbotResponseCounts: undefined,
      chatbotResData: [],
      minYear: undefined,
      maxYear: undefined,
      legend: null,
      trailNamesInDropdown: [],
      loading: false,
      tempYearRange: [this.$store.getters.getYearRange[0], this.$store.getters.getYearRange[1]],
    };
  },
  computed: {
    visibleTabGroup() {
      return this.$store.getters.getVisibleTabGroup;
    },
    selectedSource() {
      return this.$store.getters.getSelectedSource;
    },
    showChatbotMapCondition() {
      return (
        this.visibleTabGroup === "visitorCharacteristics" &&
        this.selectedSource === "chatbot" &&
        this.chatbotResData.length > 0
      );
    },
    yearRange: {
      get() {
        return this.$store.getters.getYearRange;
      },
      set(newRange) {
        this.$store.dispatch('setYearRange', newRange);
      }
    },
  },
  watch: {
    visibleTabGroup() {
      this.onTabChange();
    },
    selectedSource() {
      this.onTabChange();
    }
  },
  mounted() {
    let self = this;

    const mapDiv = L.map(self.$refs["mapDiv"], {
      center: [40.53, -99.1],
      zoom: 5,
    });

    const outdoorLayer = L.tileLayer(MAPBOX_CONSTS.TILES_API, {
      attribution: MAPBOX_CONSTS.ATTRIBUTION,
      tileSize: 512,
      maxZoom: 18,
      zoomOffset: -1,
      id: "woodsp/ckoayirck08k618p28tlyok8j",
      accessToken: MAPBOX_CONSTS.OUTDOOR_STYLE_TOKEN,
    });

    // const streetsLayer = L.tileLayer(MAPBOX_CONSTS.TILES_API, {
    //   attribution: MAPBOX_CONSTS.ATTRIBUTION,
    //   tileSize:512,
    //   maxZoom: 18,
    //   zoomOffset: -1,
    //   id: "mapbox/streets-v11",
    //   accessToken: MAPBOX_CONSTS.TOKEN
    // });

    const satelliteLayer = L.tileLayer(MAPBOX_CONSTS.TILES_API, {
      attribution: MAPBOX_CONSTS.ATTRIBUTION,
      tileSize: 512,
      maxZoom: 18,
      zoomOffset: -1,
      id: "mapbox/satellite-v9",
      accessToken: MAPBOX_CONSTS.TOKEN,
    });

    L.control
      .layers({ outdoor: outdoorLayer, satellite: satelliteLayer })
      .addTo(mapDiv);
    outdoorLayer.addTo(mapDiv);

    self.mapDiv = mapDiv;

    EventBus.$on("top-bar:site-selected", self.selectSite);
    EventBus.$on("top-bar:site-search-results", self.searchSite);
  },
  beforeDestroy() {
    let self = this;
    EventBus.$off("top-bar:site-selected", self.selectSite);
    EventBus.$off("top-bar:site-search-results", self.searchSite);
  },
  methods: {
    removeLegend() {
      if (this.legend !== null) {
        this.legend.remove();
        this.legend = null;
      }
    },
    addLegend() {
      if (this.legend === null) {
        this.legend = L.control({ position: "bottomright" });

        this.legend.onAdd = function() {
          // Create a container for your legend
          const div = L.DomUtil.create("div", "info legend");
          div.innerHTML = `
          <div style="background-color: white; padding: 10px; border-radius: 4px; line-height: 1.4em;">
            <div style="margin-bottom: 12px;">
              <span style="font-size: 14px; font-weight: bold; color: #333; text-align: center; display: block;">Polygon Colors</span>
              <div class="legend-item" style="display: flex; align-items: center; margin-bottom: 4px;">
                <!-- Red polygon -->
                <svg width="22" height="22" style="margin-right: 6px;">
                  <polygon points="5,5 15,5 15,15 5,15"
                          style="fill:${
                            solidDefaultStyle.fillColor
                          };fill-opacity:${
            solidDefaultStyle.fillOpacity
          };stroke:${solidDefaultStyle.color};stroke-width:${
            solidDefaultStyle.weight
          }"/>
                </svg>
                <span style="font-size: 13px;">With chatbot responses</span>
              </div>

              <div class="legend-item" style="display: flex; align-items: center; margin-bottom: 4px;">
                <!-- Grey polygon -->
                <svg width="22" height="22" style="margin-right: 6px;">
                  <polygon points="5,5 15,5 15,15 5,15"
                          style="fill:${
                            solidGreyStyle.fillColor
                          };fill-opacity:${solidGreyStyle.fillOpacity};stroke:${
            solidGreyStyle.color
          };stroke-width:${solidGreyStyle.weight}"/>
                </svg>
                <span style="font-size: 13px;">Without chatbot responses</span>
              </div>
            </div>

            <div>
              <span style="font-size: 14px; font-weight: bold; color: #333; text-align: center; display: block;">Bubble Sizes</span>
              <div class="legend-item" style="display: flex; align-items: center; margin-bottom: 4px;">
                <!-- Large bubble -->
                <svg width="22" height="22" style="margin-right: 6px;">
                  <circle cx="10" cy="12" r="8"
                          style="fill:${
                            bubbleDefaultStyle.fillColor
                          };fill-opacity:${
            bubbleDefaultStyle.fillOpacity
          };stroke:${bubbleDefaultStyle.color};stroke-width:${
            bubbleDefaultStyle.weight
          }"/>
                </svg>
                <span style="font-size: 13px;">More chatbot responses</span>
              </div>

              <div class="legend-item" style="display: flex; align-items: center;">
                <!-- Small bubble -->
                <svg width="22" height="22" style="margin-right: 6px;">
                  <circle cx="10" cy="10" r="4"
                          style="fill:${
                            bubbleDefaultStyle.fillColor
                          };fill-opacity:${
            bubbleDefaultStyle.fillOpacity
          };stroke:${bubbleDefaultStyle.color};stroke-width:${
            bubbleDefaultStyle.weight
          }"/>
                </svg>
                <span style="font-size: 13px;">Less chatbot responses</span>
              </div>
            </div>
          </div>

          `;

          return div;
        };
      }
      // Finally, add the legend to the map
      this.legend.addTo(this.mapDiv);
    },
    onYearRangeChange() {
      this.$store.dispatch('setYearRange', this.tempYearRange);
      this.chatbotResponseCounts = this.filterChatbotData();
      this.updateBubblesLayer();
      // this.changeToChatbotSites();
      this.searchSite([]); // either functions work, but refactor one or the other: this.changeToChatbotSites();
    },
    onTabChange() {
      this.resetStyle(this.sitesLayer);
      if (this.showChatbotMapCondition) {
        this.addbubblesLayer();
        this.addLegend();
      } else {
        this.removebubblesLayer();
        this.removeLegend();
      }
    },
    showChatbotMap() {
      this.changeToChatbotSites();
      this.addbubblesLayer();
    },
    showBasicMap() {
      this.removebubblesLayer();
      this.changeToBasicSites();
    },
    filterChatbotData() {
      const filteredData = {};
      this.chatbotResData.forEach((x) => {
        if (x.year >= this.yearRange[0] && x.year <= this.yearRange[1]) {
          if (!filteredData[x.trail]) {
            filteredData[x.trail] = x.count;
          } else {
            filteredData[x.trail] += x.count;
          }
        }
      });
      return filteredData;
    },
    createBubble: function(feature, latlng) {
      let data = feature["properties"]["num_responses"];

      if (!data) {
        return null;
      }
      // bubble area proportional to amount of responses
      const radius = Math.sqrt(data) * 2; // Multiply by 2 for better scaling
      return L.circleMarker(latlng, {
        pane: "bubblesPane",
        radius: radius,
        ...bubbleDefaultStyle,
      });
    },

    renderProjectSites: function() {
      this.loading = true;
      let self = this;
      let projectSites = {};
      this.createPanes();
      // remove the existing visible sites of the project
      self.sitesLayer.forEach((siteLayer) =>
        this.mapDiv.removeLayer(siteLayer)
      );
      self.bubblesLayer.forEach((siteLayer) =>
        this.mapDiv.removeLayer(siteLayer)
      );
      const requests = [
        axios.get(
          self.$apiEndpoint +
            "/projects/" +
            self.$store.getters.getSelectedProjectCode +
            "/sites/geojson"
        ),
      ];
      // Conditionally include chatbot response count data based on user role
      const loggedInUser = this.$store.getters.getLoggedInUser;
      if (loggedInUser !== "anon") {
        requests.push(
          axios.get(
            self.$apiEndpoint +
              "/projects/" +
              self.$store.getters.getSelectedProjectCode +
              "/get_annual_chatbot_response_counts"
          )
        );
      }
      axios.all(requests).then(
        axios.spread((geoJsonRes, chatbotRes) => {
          const allSitesGeoJson = geoJsonRes.data;
          this.mapDiv.fitBounds(L.geoJson(allSitesGeoJson).getBounds());
          let siteGroupsGeoJson = self.groupGeoJsonBySite(allSitesGeoJson);
          self.initializeSitesLayer(siteGroupsGeoJson, projectSites);
          // add bubble layer if chatbot data exists
          if (chatbotRes) {
            this.chatbotResData = chatbotRes.data;
            self.dataYearRange();
            self.chatbotResponseCounts = self.filterChatbotData();
            self.initializeBubblesLayer(siteGroupsGeoJson);
          }
          self.$store.dispatch("setProjectSites", projectSites);
        }))
        .finally(() => {
          this.loading = false;
        });
    },
    createPanes: function() {
      this.mapDiv.createPane("basicSitesPane");
      this.mapDiv.getPane("basicSitesPane").style.zIndex = 401;

      this.mapDiv.createPane("bubblesPane");
      this.mapDiv.getPane("bubblesPane").style.zIndex = 402;

      this.mapDiv.createPane("chatbotSitesPane");
      this.mapDiv.getPane("chatbotSitesPane").style.zIndex = 401;
    },
    dataYearRange: function() {
      const allYears = this.chatbotResData.map((x) => x.year);
      this.minYear = Math.min(...allYears);
      this.maxYear = Math.max(...allYears);
      this.yearRange = [this.minYear, this.maxYear];
      this.tempYearRange = [this.minYear, this.maxYear];
    },
    getCentroidFeatures: function(geoJsonData) {
      let centroidFeatures = [];
      geoJsonData.features.forEach((feature) => {
        let centroid = turf.centroid(feature);
        centroid.properties = {
          ...feature.properties,
          siteid: feature.properties.siteid,
          name: feature.properties.Trail_name,
        };
        centroidFeatures.push(centroid);
      });
      return centroidFeatures;
    },
    // Group geoJSON by site
    groupGeoJsonBySite: function(geoJsonData) {
      let siteGroupsGeoJson = {};
      // const selectedProjectCode = this.$store.getters.getSelectedProjectCode; //project code
      geoJsonData.features.forEach((feature) => {
        const siteid = feature.properties.siteid;
        const trailName = feature.properties.Trail_name;
        // const prjctCode = feature.properties.Prjct_code;
        // const prjctCodeList = prjctCode.split(",").map((code) => code.trim()); // checks if site is in project
        // if (prjctCodeList.includes(selectedProjectCode)) {
        if (!(siteid in siteGroupsGeoJson)) {
          siteGroupsGeoJson[siteid] = {
            type: "FeatureCollection",
            name: trailName,
            siteid: siteid,
            features: [],
          };
        }
        siteGroupsGeoJson[siteid].features.push(feature);
        // }
      });
      return siteGroupsGeoJson;
    },
    // Add basic sites layer
    initializeSitesLayer: function(siteGroupsGeoJson, projectSites) {
      Object.entries(siteGroupsGeoJson).forEach(([, site]) => {
        const isDuplicate =
          Object.values(siteGroupsGeoJson).filter((s) => s.name === site.name)
            .length > 1;
        const trailName = isDuplicate
          ? `${site.name} (${site.siteid})`
          : site.name;
        let siteLayer = L.geoJSON(site, {
          pane: "basicSitesPane",
          style: defaultStyle,
        })
          .bindTooltip(trailName)
          .on("mouseover", this.handleMouseOver)
          .on("mouseout", this.handleMouseOut)
          .on("click", this.handleClick);

        siteLayer.siteid = site.siteid;
        siteLayer.trailName = trailName;
        projectSites[siteLayer.siteid] = siteLayer;
        this.sitesLayer.push(siteLayer);
        siteLayer.addTo(this.mapDiv);
      });
    },
    initializeBubblesLayer: function(siteGroupsGeoJson) {
      // Sort sites by response count in descending order
      const sortedSites = Object.entries(siteGroupsGeoJson).sort(
        ([, siteA], [, siteB]) => {
          const responsesA = this.chatbotResponseCounts[siteA.siteid] || 0;
          const responsesB = this.chatbotResponseCounts[siteB.siteid] || 0;
          return responsesB - responsesA; // Descending order
        }
      );

      sortedSites.forEach(([, site]) => {
        const siteid = site.siteid;
        const num_responses = this.chatbotResponseCounts[siteid] || 0;
        const isDuplicate =
          Object.values(siteGroupsGeoJson).filter((s) => s.name === site.name)
            .length > 1;
        const trailName = isDuplicate
          ? `${site.name} (${site.siteid})`
          : site.name;
        const centroid = turf.centroid(site);
        centroid.properties = {
          // siteid: site.siteid,
          num_responses: num_responses,
        };
        let centroidLayer = L.geoJSON(centroid, {
          pane: "bubblesPane",
          pointToLayer: this.createBubble,
        })
          .bindTooltip(`${trailName}: ${num_responses} responses`)
          .on("mouseover", this.handleMouseOver)
          .on("mouseout", this.handleMouseOut)
          .on("click", this.handleClick);

        // Assign properties to the layer
        centroidLayer.siteid = site.siteid;
        centroidLayer.trailName = trailName;
        this.bubblesLayer.push(centroidLayer);
        this.onTabChange();
      });
    },
    addbubblesLayer: function() {
      this.bubblesLayer.forEach((layer) => {
        if (!this.mapDiv.hasLayer(layer)) {
          layer.addTo(this.mapDiv);
        }
      });
    },
    removebubblesLayer: function() {
      this.bubblesLayer.forEach((layer) => {
        if (this.mapDiv.hasLayer(layer)) {
          this.mapDiv.removeLayer(layer);
        }
      });
    },
    updateBubblesLayer: function() {
      // Sort sites by response count in descending order
      const sortedBubblesLayers = this.bubblesLayer.sort((layerA, layerB) => {
        const responsesA = this.chatbotResponseCounts[layerA.siteid] || 0;
        const responsesB = this.chatbotResponseCounts[layerB.siteid] || 0;
        return responsesB - responsesA;
      });
      sortedBubblesLayers.forEach((layer) => {
        if (layer.eachLayer) {
          const trailName = layer.trailName;
          const siteid = layer.siteid;
          const num_responses = this.chatbotResponseCounts[siteid] || 0;
          layer.eachLayer((circleMarker) => {
            if (circleMarker instanceof L.CircleMarker) {
              const radius = Math.sqrt(num_responses) * 2;
              circleMarker.setRadius(radius);
              if (num_responses == 0) {
                circleMarker.setStyle({ fill: false, stroke: false });
              } else {
                circleMarker.setStyle({ fill: true, stroke: true });
              }
            }
          });
          layer.bindTooltip(`${trailName}: ${num_responses} responses`);
        }
      });
    },
    // Mouse event handlers
    handleMouseOver: function(event) {
      if (
        event.target.siteid !== this.$store.getters.getSelectedSite.siteid &&
        event.target.siteid !== this.$store.getters.getComparingSite.siteid
      ) {
        const siteid = event.target.siteid;
        const site = this.sitesLayer.find((layer) => layer.siteid == siteid);
        if (site) {
          site.setStyle({
            ...hoverStyle,
          });
        }
        const circleMarker = this.bubblesLayer.find(
          (layer) => layer.siteid === siteid
        );
        if (circleMarker) {
          circleMarker.setStyle({
            ...hoverStyle,
          });
        }
      }
    },
    handleMouseOut: function(event) {
      this.resetStyle([event.target]);
    },
    handleClick: function(event) {
      if (event.originalEvent.ctrlKey) {
        if (
          this.$store.getters.getComparingSite &&
          this.$store.getters.getSelectedSite
        ) {
          this.showAlert();
        } else if (this.$store.getters.getSelectedSite) {
          this.$store.dispatch("setComparingSite", event.target);
          this.resetStyle([this.$store.getters.getSelectedSite]);
          this.resetStyle([this.$store.getters.getComparingSite]);
          EventBus.$emit("map-div:compare-activated");
        }
      } else {
        this.selectSite(event.target);
      }
    },
    selectSite: function(target) {
      const siteID = target.siteid;
      let self = this;
      if (self.$store.getters.getComparingSite) {
        self.$store.dispatch("setComparingSite", "");
      }
      if (self.$store.getters.getSelectedSite) {
        self.$store.dispatch("setSelectedSite", "");
      }
      let site = this.sitesLayer.find((layer) => layer.siteid === siteID);
      self.$store.dispatch("setSelectedSite", site);
      EventBus.$emit("map-div:site-selected");
      this.mapDiv.fitBounds(site.getBounds(), { maxZoom: 11 });
      this.resetStyle(this.sitesLayer);
    },
    searchSite: function(trailNamesList) {
      this.trailNamesInDropdown = trailNamesList;
      this.resetStyle(this.sitesLayer);
    },
    resetStyle: function(sitesList) {
      const selectedSite = this.$store.getters.getSelectedSite;
      const comparingSite = this.$store.getters.getComparingSite;
      sitesList.forEach((site) => {
        const siteid = site.siteid;

        const sitePolygon = this.sitesLayer.find(
          (layer) => layer.siteid == siteid
        );
        const bubble = this.bubblesLayer.find(
          (layer) => layer.siteid === siteid
        );
        let siteStyle = defaultStyle;
        let bubbleStyle = bubbleDefaultStyle;
        if (this.trailNamesInDropdown.includes(site.trailName)) {
          bubbleStyle = bubbleHighlightStyle;
          siteStyle = highlightStyle;
        } else if (
          siteid !== this.$store.getters.getSelectedSite.siteid &&
          siteid !== this.$store.getters.getComparingSite.siteid
        ) {
          if (this.showChatbotMapCondition) {
            const estimate = this.chatbotResponseCounts[site.siteid] || 0;
            siteStyle = estimate === 0 ? solidGreyStyle : solidDefaultStyle;
          } else {
            siteStyle = defaultStyle;
          }
          bubbleStyle = bubbleDefaultStyle;
        } else {
          if (selectedSite && comparingSite) {
            siteStyle = compareStyle;
            bubbleStyle = compareStyle;
          }
          // check if need to restore selected site style
          else if (selectedSite) {
            siteStyle = selectedStyle;
            bubbleStyle = selectedStyle;
          }
        }
        if (sitePolygon) {
          sitePolygon.setStyle(siteStyle);
        }
        if (bubble) {
          bubble.setStyle(bubbleStyle);
        }
      });
    },
    countDownChanged(dismissCountDown) {
      this.dismissCountDown = dismissCountDown;
    },
    showAlert() {
      this.dismissCountDown = this.dismissSecs;
    },
  },
};
</script>

<style scoped>
@import "~leaflet/dist/leaflet.css";

.map-div .leaflet-tile {
  filter: brightness(0.5) contrast(1.1) saturate(0.8) !important;
}

.map-root {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.range-slider-container {
  position: absolute;
  bottom: 19%;
  left: 1%;
  z-index: 1000;
  width: 50%;
  height: 50px;
}
</style>
