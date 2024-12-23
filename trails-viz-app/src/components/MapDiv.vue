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
    fillColor: "#ff0000",
    fillOpacity: 1,
    weight: 1
  };

  const greyedStyle = {
    color: '#808080',
    fillColor: '#808080',
    weight: 1,
    fillOpacity: 1
  }

  const hoverStyle = {
    color: "#ffb801",
    weight: 0.8
  };

  const selectedStyle = {
    color: "#0000ff",
    weight: 0.8
  };

  const compareStyle = {
    color: "#fa00ff",
    weight: 0.8
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
      onTabGroupChange(group) {
        console.log(`Visible Tab Group changed to: ${group}`);
        if (group === 'visitorCharacteristics') {
          this.chatbotActivityLayer.forEach((layer) => {
            if (!this.mapDiv.hasLayer(layer)) {
              layer.addTo(this.mapDiv)
            }
          })

          this.chatbotSitesLayer.forEach((layer) => {
            if (!this.mapDiv.hasLayer(layer)) {
              layer.addTo(this.mapDiv)
            }
          })

          this.basicSitesLayer.forEach((layer) => {
            if (this.mapDiv.hasLayer(layer)) {
              this.mapDiv.removeLayer(layer)
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
      _pointToMarker: function(feature, latlng) {
        // console.log("Feature:", feature, "LatLng:", latlng)
        let self = this;
        let siteid = feature['properties']['siteid'];
        let estimate = self.lastYearEstimates[siteid];

        if (!estimate) {
          return null;
        }
        // Calculate radius proportional to the estimate (adjust scaling factor as needed)
        const radius = Math.sqrt(estimate) * 2; // Adjust multiplier for better scaling

        return L.circleMarker(latlng, {
          pane: 'circlesPane',
          radius: radius,
          color: "#3388ff", // Border color
          weight: 1, // Border width
          fillColor: "#3388ff", // Fill color
          fillOpacity: 1, // Transparency
        }).bindTooltip(`${feature.properties.name}: ${estimate}`);

        // let iconUrl = 'data:image/svg+xml;base64,' + btoa(MARKER.replace('{fillMe}', self.getColor(estimate)));
        // console.log("Generated iconUrl:", iconUrl)
        // let icon = new IconSuper({iconUrl: iconUrl});
        // return L.marker(latlng, {icon: icon});
      },
      renderProjectSites: function () {
        let self = this;
        let projectSites = {};
        let centroidFeatures = [];

        this.mapDiv.createPane('basicSitesPane');
        this.mapDiv.getPane('basicSitesPane').style.zIndex = 402;

        this.mapDiv.createPane('circlesPane');
        this.mapDiv.getPane('circlesPane').style.zIndex = 401;

        this.mapDiv.createPane('chatbotSitesPane');
        this.mapDiv.getPane('chatbotSitesPane').style.zIndex = 402;

        // remove the existing visible sites of the project
        self.chatbotSitesLayer.forEach(siteLayer => this.mapDiv.removeLayer(siteLayer));

        axios.all([
          axios.get(self.$apiEndpoint + '/projects/' + self.$store.getters.getSelectedProjectCode + '/sites/geojson'),
          axios.get(self.$apiEndpoint + '/projects/' + self.$store.getters.getSelectedProjectCode + '/lastYearEstimates'),
          axios.get(self.$apiEndpoint + '/projects/' + self.$store.getters.getSelectedProjectCode + '/get_annual_chatbot_response_counts')
          ]).then(axios.spread((geoJsonRes, estimatesRes, chatbotRes) => {
            let allSitesGeoJson = geoJsonRes.data;
            let lastYearEstimates = {};
            let siteGroupsGeoJson = {};
            let chatbotResponseCounts = {};

            estimatesRes.data.forEach(x => lastYearEstimates[x.trail] = x.estimate);
            self.lastYearEstimates = lastYearEstimates;

            // Extract all years from chatbotRes data
            const allYears = chatbotRes.data.map(x => x.year);
            self.minYear = Math.min(...allYears);
            self.maxYear = Math.max(...allYears);
            self.yearRange = [self.minYear, self.maxYear];

            console.log("Calculated Year Range:", self.yearRange);

            chatbotRes.data.forEach((x) => {
              if (x.year >= self.minYear && x.year <= self.maxYear) {
                if (!chatbotResponseCounts[x.trail]) {
                  chatbotResponseCounts[x.trail] = x.count;
                }
                else {
                  chatbotResponseCounts[x.trail] += x.count;
                }
              }
            });
            console.log('chatbotResponseCounts:', chatbotResponseCounts)
            self.lastYearEstimates = chatbotResponseCounts
            self.chatbotResponseCounts = chatbotResponseCounts
            // calculate centroids
            allSitesGeoJson.features.forEach((feature) => {
              let centroid = turf.centroid(feature);
              centroid.properties = {
                ...feature.properties,
                siteid: feature.properties.siteid,
                name: feature.properties.Trail_name
              };
              centroidFeatures.push(centroid);
            })
            // console.log('centroidFeatures:',centroidFeatures)

            this.mapDiv.fitBounds(L.geoJson(allSitesGeoJson).getBounds());

            for (let feature of allSitesGeoJson["features"]) {
              let siteid = feature["properties"]["siteid"];
              let trailName = feature["properties"]["Trail_name"];

              if (!(siteid in siteGroupsGeoJson)) {
                siteGroupsGeoJson[siteid] = {"type": "FeatureCollection", "name": trailName, "siteid": siteid};
                siteGroupsGeoJson[siteid]["features"] = [];
              }
              siteGroupsGeoJson[siteid]["features"].push(feature);
            }
            
            let centroidLayer = L.geoJSON({ type: "FeatureCollection", features: centroidFeatures }, {
                pointToLayer: self._pointToMarker // Use your custom point marker logic
              }
            ).bindTooltip(layer => layer.feature.properties.name); // Tooltip for name
            self.chatbotActivityLayer.push(centroidLayer);
            if (self.visibleTabGroup === 'visitorCharacteristics') {
              centroidLayer.addTo(self.mapDiv); // Add the centroid layer to the map
            }
            self.$store.dispatch('setProjectSites', projectSites);
            Object.entries(siteGroupsGeoJson).forEach(([, site]) => {
              // console.log("site:", site)
              let siteLayer = L.geoJSON(site, {
                pane: 'chatbotSitesPane',
                style: function (feature) {
                  const siteid = feature.properties.siteid
                  const estimate = self.lastYearEstimates[siteid] || 0;
                  return estimate === 0 ? greyedStyle : defaultStyle
                }
              })
                .bindTooltip(site["name"])
                .on('mouseover', function (event) {
                  if (event.target === self.$store.getters.getSelectedSite || event.target === self.$store.getters.getComparingSite) {
                    // do nothing
                  } else {
                    event.target.setStyle(hoverStyle);
                  }
                })
                .on('mouseout', function (event) {
                  if (event.target === self.$store.getters.getSelectedSite || event.target === self.$store.getters.getComparingSite) {
                    // don't change the style
                  } else {
                    const estimate = self.lastYearEstimates[event.target.siteid] || 0;
                    estimate === 0
                      ? event.target.setStyle(greyedStyle)
                      : event.target.setStyle(defaultStyle);
                  }
                })
                .on('click', function (event) {
                  if (event.originalEvent.ctrlKey) {
                    if (self.$store.getters.getComparingSite && self.$store.getters.getSelectedSite) {
                      self.showAlert();
                    }
                    else if(self.$store.getters.getSelectedSite) {
                      self.$store.dispatch('setComparingSite', event.target);
                      self.$store.getters.getSelectedSite.setStyle(compareStyle);
                      self.$store.getters.getComparingSite.setStyle(compareStyle);
                      EventBus.$emit('map-div:compare-activated');
                    }
                  } else {
                    self.selectSite(event.target["trailName"])
                  }
                });
              // custom properties can be added to JS objects
              siteLayer.siteid = site["siteid"];
              siteLayer.trailName = site["name"];

              self.chatbotSitesLayer.push(siteLayer);
              projectSites[siteLayer.trailName] = siteLayer;
              if (self.visibleTabGroup === 'visitorCharacteristics') {
                siteLayer.addTo(self.mapDiv);
              }
            });

            Object.entries(siteGroupsGeoJson).forEach(([, site]) => {
              let siteLayer = L.geoJSON(site, {pane: 'basicSitesPane', style: defaultStyle})
                .bindTooltip(site["name"])
                .on('mouseover', function (event) {
                  if (event.target === self.$store.getters.getSelectedSite || event.target === self.$store.getters.getComparingSite) {
                    // do nothing
                  } else {
                    event.target.setStyle(hoverStyle);
                  }
                })
                .on('mouseout', function (event) {
                  if (event.target === self.$store.getters.getSelectedSite || event.target === self.$store.getters.getComparingSite) {
                    // don't change the style
                  } else {
                    event.target.setStyle(defaultStyle);
                  }
                })
                .on('click', function (event) {
                  if (event.originalEvent.ctrlKey) {
                    if (self.$store.getters.getComparingSite && self.$store.getters.getSelectedSite) {
                      self.showAlert();
                    }
                    else if(self.$store.getters.getSelectedSite) {
                      self.$store.dispatch('setComparingSite', event.target);
                      self.$store.getters.getSelectedSite.setStyle(compareStyle);
                      self.$store.getters.getComparingSite.setStyle(compareStyle);
                      EventBus.$emit('map-div:compare-activated');
                    }
                  } else {
                    self.selectSite(event.target["trailName"])
                  }
                });

              // custom properties can be added to JS objects
              siteLayer.siteid = site["siteid"];
              siteLayer.trailName = site["name"];

              self.basicSitesLayer.push(siteLayer);
              projectSites[siteLayer.trailName] = siteLayer;
              siteLayer.addTo(self.mapDiv);
              if (self.visibleTabGroup !== 'visitorCharacteristics') {
                siteLayer.addTo(self.mapDiv);
              }
            });
        }))
      },
      selectSite: function (trailName) {
        let self = this;
        if (self.$store.getters.getComparingSite) {
          self.$store.getters.getComparingSite.setStyle(defaultStyle);
          self.$store.dispatch('setComparingSite', '');
        }
        if (self.$store.getters.getSelectedSite) {
          self.$store.getters.getSelectedSite.setStyle(defaultStyle);
        }
        let site = self.$store.getters.getProjectSites[trailName];
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
