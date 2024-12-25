<template>
  <div>
    <b-alert :show="dismissCountDown" dismissible fade variant="warning" @dismiss-count-down="countDownChanged">
      Only two sites can be compared at a time!
    </b-alert>
    <div>
      <p>Current Tab: {{ visibleTabGroup  }}</p>
    </div>
    <!-- Range Slider for Year Selection -->
    <div>
      <v-app>
        <v-card>
          <v-card-text>
            <v-range-slider
              v-if="yearRange && minYear !== undefined && maxYear !== undefined"
              v-model="yearRange"
              :min="minYear"
              :max="maxYear"
              ticks
              step="1"
              thumb-label
              @change="onYearRangeChange"
            >
              <template v-slot:prepend>
                <span>{{ yearRange[0] }}</span>
              </template>
              <template v-slot:append>
                <span>{{ yearRange[1] }}</span>
              </template>
            </v-range-slider>
          </v-card-text>
        </v-card>
        <div class="map-div" ref="mapDiv"></div>
      </v-app>
    </div>
  </div>
</template>


<script>
  import L from "leaflet";
  import axios from "axios";
  import {MAPBOX_CONSTS} from "../store/constants";
  import {MARKER} from "../store/vectors";
  import {EventBus} from "../event-bus";
  import * as turf from "@turf/turf";

  // The following two statements are required because of an issue with leaflet and webpack
  // see https://github.com/Leaflet/Leaflet/issues/4968#issuecomment-483402699
  delete L.Icon.Default.prototype._getIconUrl;

  L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
  });

  // Make the fault marker of leaflet smaller
  L.Icon.Default.prototype.options.iconAnchor = [6, 20];
  L.Icon.Default.prototype.options.iconSize = [13, 20];
  L.Icon.Default.prototype.options.shadowSize = [20, 20];

  // Update icon URL to use the SVG
  let IconSuper = L.Icon.extend({
    options: L.Icon.Default.prototype.options
  });

  const defaultStyle = {
    color: "#ff0000",
    weight: 1,
    fillColor: '#ff0000',
    fillOpacity: 0.2
  };

  const solidDefaultStyle = {
    color: "#ff0000",
    weight: 1,
    fillColor: '#ff0000',
    fillOpacity: 1
  };

  const solidGreyStyle = {
    color: '#808080',
    weight: 1,
    fillColor: '#808080',
    fillOpacity: 1
  };

  const hoverStyle = {
    color: "#ffb801",
    weight: 0.8,
    fillColor: '#ffb801',
    fillOpacity: 0.2
  };

  const selectedStyle = {
    color: "#0000ff",
    weight: 0.8,
    fillColor: '#0000ff',
    fillOpacity: 0.2
  };

  const compareStyle = {
    color: "#fa00ff",
    weight: 0.8,
    fillColor: '#fa00ff',
    fillOpacity: 0.2
  };

  export default {
    name: "MapDiv",
    props: {
      visibleTabGroup: {
        type: String,
        required: true,
      },
    },
    data: function() {
      return {
        dismissSecs: 5,
        dismissCountDown: 0,
        basicSitesLayer : [],
        chatbotSitesLayer : [],
        chatbotActivityLayer : [],
        lastYearEstimates: undefined,
        chatbotResponseCounts: undefined,
        chatbotResData: undefined,
        yearRange: [], // Default range
        minYear: undefined,
        maxYear: undefined,
      }
    },
    watch: {
      visibleTabGroup(newGroup) {
        this.onTabGroupChange(newGroup);
      },
    },
    mounted() {
      let self = this;

      const mapDiv = L.map(self.$refs["mapDiv"], {
        center: [40.53, -99.1],
        zoom: 5
      });

      const outdoorLayer = L.tileLayer(MAPBOX_CONSTS.TILES_API, {
        attribution: MAPBOX_CONSTS.ATTRIBUTION,
        tileSize:512,
        maxZoom: 18,
        zoomOffset: -1,
        id: "woodsp/ckoayirck08k618p28tlyok8j",
        accessToken: MAPBOX_CONSTS.OUTDOOR_STYLE_TOKEN
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
        tileSize:512,
        maxZoom: 18,
        zoomOffset: -1,
        id: "mapbox/satellite-v9",
        accessToken: MAPBOX_CONSTS.TOKEN
      });

      L.control.layers({"outdoor": outdoorLayer, "satellite": satelliteLayer}).addTo(mapDiv);
      outdoorLayer.addTo(mapDiv);

      self.mapDiv = mapDiv;

      EventBus.$on('top-bar:site-selected', self.selectSite);
    },
    beforeDestroy() {
      let self = this;
      EventBus.$off('top-bar:site-selected', self.selectSite);
    },
    methods: {
      onYearRangeChange() {
        console.log("year range changed:", this.yearRange)
        const filteredData = this.filterChatbotData();
        this.chatbotResponseCounts = { ...filteredData };
        this.updateMapLayers();
      },
      onTabGroupChange(group) {
        console.log(`Visible Tab Group changed to: ${group}`);
        if (group === 'visitorCharacteristics') {
          this.basicSitesLayer.forEach((layer) => {
            if (this.mapDiv.hasLayer(layer)) {
              this.mapDiv.removeLayer(layer)
            }
          })
          this.chatbotSitesLayer.forEach((layer) => {
            if (!this.mapDiv.hasLayer(layer)) {
              layer.addTo(this.mapDiv)
            }
          })
          this.chatbotActivityLayer.forEach((layer) => {
            if (!this.mapDiv.hasLayer(layer)) {
              layer.addTo(this.mapDiv)
            }
          })
        } 
        else {
          this.chatbotActivityLayer.forEach((layer) => {
            if (this.mapDiv.hasLayer(layer)) {
              this.mapDiv.removeLayer(layer)
            }
          })
          this.chatbotSitesLayer.forEach((layer) => {
            if (this.mapDiv.hasLayer(layer)) {
              this.mapDiv.removeLayer(layer)
            }
          })
          this.basicSitesLayer.forEach((layer) => {
            if (!this.mapDiv.hasLayer(layer)) {
              layer.addTo(this.mapDiv)
            }
          })
        }
        // Handle tab group changes, e.g., update the map view or layers
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
      createCircleMarker: function(feature, latlng) {
        let self = this;
        let siteid = feature['properties']['siteid'];
        let data = self.chatbotResponseCounts[siteid];

        if (!data) {
          return null;
        }
        // Calculate radius proportional to the estimate (adjust scaling factor as needed)
        const radius = Math.sqrt(data) * 2; // Adjust multiplier for better scaling
        return L.circleMarker(latlng, {
          pane: 'circlesPane',
          radius: radius,
          color: "#3388ff", // Border color
          weight: 1, // Border width
          fillColor: "#3388ff", // Fill color
          fillOpacity: 1, // Transparency
        }).bindTooltip(`${feature.properties.name}: ${data}`);
      },


      renderProjectSites: function () {
        let self = this;
        let projectSites = {
          basicSites:{},
          chatbotSites:{},
        };
        let centroidFeatures = [];

        this.createPanes();

        // remove the existing visible sites of the project
        self.chatbotSitesLayer.forEach(siteLayer => this.mapDiv.removeLayer(siteLayer));
        self.basicSitesLayer.forEach(siteLayer => this.mapDiv.removeLayer(siteLayer));
        self.chatbotActivityLayer.forEach(siteLayer => this.mapDiv.removeLayer(siteLayer))

        axios
        .all([
          axios.get(
            self.$apiEndpoint + '/projects/' + self.$store.getters.getSelectedProjectCode + '/sites/geojson'
          ),
          axios.get(
            self.$apiEndpoint + '/projects/' + self.$store.getters.getSelectedProjectCode + '/lastYearEstimates'
          ),
          axios.get(
            self.$apiEndpoint + '/projects/' + self.$store.getters.getSelectedProjectCode + 
            '/get_annual_chatbot_response_counts'
          ),
        ])
        .then(
            axios.spread((geoJsonRes, estimatesRes, chatbotRes) => {
            const allSitesGeoJson = geoJsonRes.data;
            this.chatbotResData = chatbotRes.data

            self.processYearRange(chatbotRes.data);
            self.chatbotResponseCounts = self.filterChatbotData();

            centroidFeatures = self.getCentroidFeatures(allSitesGeoJson);
            
            this.mapDiv.fitBounds(L.geoJson(allSitesGeoJson).getBounds());

            let siteGroupsGeoJson = self.groupGeoJsonBySite(allSitesGeoJson);

            self.addBasicSitesLayer(siteGroupsGeoJson, projectSites); // Add basic sites layer logic
            self.addChatbotAcitivityLayer(centroidFeatures); // Add centroid layer logic
            self.addChatbotSitesLayer(siteGroupsGeoJson, projectSites); // Add chatbot sites layer logic
            
            self.$store.dispatch('setProjectSites', projectSites);
            let site = self.$store.getters.getProjectSites(self.visibleTabGroup);
            console.log('site:', site)
        }))
      },
      createPanes: function () {
        this.mapDiv.createPane("basicSitesPane");
        this.mapDiv.getPane("basicSitesPane").style.zIndex = 402;

        this.mapDiv.createPane("circlesPane");
        this.mapDiv.getPane("circlesPane").style.zIndex = 401;

        this.mapDiv.createPane("chatbotSitesPane");
        this.mapDiv.getPane("chatbotSitesPane").style.zIndex = 402;
      },
      processYearRange: function (data) {
        const allYears = data.map((x) => x.year);
        this.minYear = Math.min(...allYears);
        this.maxYear = Math.max(...allYears);
        this.yearRange = [this.minYear, this.maxYear];
        console.log("Calculated Year Range:", this.yearRange);
      },
      getCentroidFeatures: function (geoJsonData) {
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
      groupGeoJsonBySite: function (geoJsonData) {
        let siteGroupsGeoJson = {};
        geoJsonData.features.forEach((feature) => {
          const siteid = feature.properties.siteid;
          const trailName = feature.properties.Trail_name;

          if (!(siteid in siteGroupsGeoJson)) {
            siteGroupsGeoJson[siteid] = {
              type: "FeatureCollection",
              name: trailName,
              siteid: siteid,
              features: [],
            };
          }
          siteGroupsGeoJson[siteid].features.push(feature);
        });
        return siteGroupsGeoJson;
      },
      addChatbotAcitivityLayer: function (centroidFeatures) {
        const centroidLayer = L.geoJSON(
          { type: "FeatureCollection", features: centroidFeatures },
          { pointToLayer: this.createCircleMarker }
        ).bindTooltip((layer) => layer.feature.properties.name);

        this.chatbotActivityLayer.push(centroidLayer);
        if (this.visibleTabGroup === "visitorCharacteristics") {
          centroidLayer.addTo(this.mapDiv); // Add the centroid layer to the map
        }
      },
      // Add chatbot sites layer
      addChatbotSitesLayer: function (siteGroupsGeoJson, projectSites) {
        Object.entries(siteGroupsGeoJson).forEach(([, site]) => {
          let siteLayer = L.geoJSON(site, {
            pane: "chatbotSitesPane",
            style: (feature) => {
              const siteid = feature.properties.siteid;
              const estimate = this.chatbotResponseCounts[siteid] || 0;
              return estimate === 0 ? solidGreyStyle : solidDefaultStyle;
            },
          })
            .bindTooltip(site.name)
            .on("mouseover", this.handleMouseOver)
            .on("mouseout", this.handleMouseOutChatbotSitesLayer)
            .on("click", this.handleClick);

          siteLayer.siteid = site.siteid;
          siteLayer.trailName = site.name;

          this.chatbotSitesLayer.push(siteLayer);
          projectSites.chatbotSites[siteLayer.trailName] = siteLayer;
          if (this.visibleTabGroup === "visitorCharacteristics") {
            siteLayer.addTo(this.mapDiv);
          }
        });
      },
      // Add basic sites layer
      addBasicSitesLayer: function (siteGroupsGeoJson, projectSites) {
        Object.entries(siteGroupsGeoJson).forEach(([, site]) => {
          let siteLayer = L.geoJSON(site, {
            pane: "basicSitesPane",
            style: defaultStyle,
          })
            .bindTooltip(site.name)
            .on("mouseover", this.handleMouseOver)
            .on("mouseout", this.handleMouseOutBasicSitesLayer)
            .on("click", this.handleClick);

          siteLayer.siteid = site.siteid;
          siteLayer.trailName = site.name;

          this.basicSitesLayer.push(siteLayer);
          projectSites.basicSites[siteLayer.trailName] = siteLayer;
          if (this.visibleTabGroup !== "visitorCharacteristics") {
            siteLayer.addTo(this.mapDiv);
          }
        });
      },
      // Mouse event handlers
      handleMouseOver: function (event) {
        if (
          event.target !== this.$store.getters.getSelectedSite &&
          event.target !== this.$store.getters.getComparingSite
        ) {
          event.target.setStyle(hoverStyle);
        }
      },
      handleMouseOutChatbotSitesLayer: function (event) {
        if (
          event.target !== this.$store.getters.getSelectedSite &&
          event.target !== this.$store.getters.getComparingSite
        ) {
          const estimate =
            this.chatbotResponseCounts[event.target.siteid] || 0;
          event.target.setStyle(
            estimate === 0 ? solidGreyStyle : solidDefaultStyle
          );
        }
      },
      handleMouseOutBasicSitesLayer: function (event) {
        if (
          event.target !== this.$store.getters.getSelectedSite &&
          event.target !== this.$store.getters.getComparingSite
        ) {
          event.target.setStyle(defaultStyle);
        }
      },
      handleClick: function (event) {
        if (event.originalEvent.ctrlKey) {
          if (
            this.$store.getters.getComparingSite &&
            this.$store.getters.getSelectedSite
          ) {
            this.showAlert();
          } else if (this.$store.getters.getSelectedSite) {
            this.$store.dispatch("setComparingSite", event.target);
            this.$store.getters.getSelectedSite.setStyle(compareStyle);
            this.$store.getters.getComparingSite.setStyle(compareStyle);
            EventBus.$emit("map-div:compare-activated");
          }
        } else {
          this.selectSite(event.target.trailName);
        }
      },
      selectSite: function (trailName) {
        let self = this;
        if (self.$store.getters.getComparingSite) {
          if (self.visibleTabGroup === 'visitorCharacteristics') {
            self.$store.getters.getComparingSite.setStyle(solidDefaultStyle);
          }
          else {
            self.$store.getters.getComparingSite.setStyle(defaultStyle);
          }
          self.$store.dispatch('setComparingSite', '');
        }
        if (self.$store.getters.getSelectedSite) {
          if (self.visibleTabGroup === 'visitorCharacteristics') {
            self.$store.getters.getSelectedSite.setStyle(solidDefaultStyle);
          }
          else {
            self.$store.getters.getSelectedSite.setStyle(defaultStyle);
          }
        }
        let site = self.$store.getters.getProjectSites(self.visibleTabGroup)[trailName];
        site.setStyle(selectedStyle);
        self.$store.dispatch('setSelectedSite', site);
        EventBus.$emit('map-div:site-selected');
        this.mapDiv.fitBounds(site.getBounds(), {maxZoom: 11});
      },
      countDownChanged(dismissCountDown) {
        this.dismissCountDown = dismissCountDown
      },
      showAlert() {
        this.dismissCountDown = this.dismissSecs
      }
    }
  }
</script>

<style scoped>
  @import "~leaflet/dist/leaflet.css";
  .map-div {
    height: 85vh;
  }
</style>
