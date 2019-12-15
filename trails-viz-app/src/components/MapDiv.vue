<template>
  <div>
    <b-alert :show="dismissCountDown" dismissible fade variant="warning" @dismiss-count-down="countDownChanged">
      Only two sites can be compared at a time!
    </b-alert>
    <div class="map-div" ref="mapDiv"></div>
  </div>
</template>

<script>
  import L from "leaflet";
  import axios from "axios";
  import {MAPBOX_CONSTS} from "../store/constants";
  import {MARKER} from "../store/vectors";
  import {EventBus} from "../event-bus";

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
    weight: 0.5
  };

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
    data: function() {
      return {
        dismissSecs: 5,
        dismissCountDown: 0,
        visibleLayers : [],
        lastYearEstimates: undefined
      }
    },
    mounted() {
      let self = this;

      const mapDiv = L.map(self.$refs["mapDiv"], {
        center: [40.53, -99.1],
        zoom: 5
      });

      const outdoorLayer = L.tileLayer(MAPBOX_CONSTS.TILES_API, {
        attribution: MAPBOX_CONSTS.ATTRIBUTION,
        maxZoom: 18,
        id: "mapbox.outdoors",
        accessToken: MAPBOX_CONSTS.TOKEN
      });

      const streetsLayer = L.tileLayer(MAPBOX_CONSTS.TILES_API, {
        attribution: MAPBOX_CONSTS.ATTRIBUTION,
        maxZoom: 18,
        id: "mapbox.streets",
        accessToken: MAPBOX_CONSTS.TOKEN
      });

      const satelliteLayer = L.tileLayer(MAPBOX_CONSTS.TILES_API, {
        attribution: MAPBOX_CONSTS.ATTRIBUTION,
        maxZoom: 18,
        id: "mapbox.satellite",
        accessToken: MAPBOX_CONSTS.TOKEN
      });

      L.control.layers({"outdoor": outdoorLayer, "streets": streetsLayer, "satellite": satelliteLayer}).addTo(mapDiv);
      outdoorLayer.addTo(mapDiv);

      self.mapDiv = mapDiv;

      EventBus.$on('top-bar:site-selected', self.selectSite);
    },
    beforeDestroy() {
      let self = this;
      EventBus.$off('top-bar:site-selected', self.selectSite);
    },
    methods: {
      _pointToMarker: function(feature, latlng) {
        let self = this;
        let siteid = feature['properties']['siteid'];
        let estimate = self.lastYearEstimates[siteid];

        let getColor = function (value) {
          if (value > 50000) {
            return '#253494';
          }
          if (value > 10000) {
            return '#2c7fb8';
          }
          if (value > 5000) {
            return '#41b6c4';
          }
          if (value > 1000) {
            return '#7fcdbb';
          }
          if (value > 500) {
            return '#c7e9b4';
          }
          if (value >= 0) {
            return '#ffffcc';
          }
        };

        let iconUrl = 'data:image/svg+xml;base64,' + btoa(MARKER.replace('{fillMe}', getColor(estimate)));
        let icon = new IconSuper({iconUrl: iconUrl});
        return L.marker(latlng, {icon: icon});
      },
      renderProjectSites: function () {
        let self = this;
        let projectSites = {};

        // remove the existing visible sites of the project
        self.visibleLayers.forEach(siteLayer => this.mapDiv.removeLayer(siteLayer));

        axios.all([
          axios.get(self.$apiEndpoint + "/sites/geojson?projectGroup=" + self.$store.getters.getSelectedProjectCode),
          axios.get(self.$apiEndpoint + '/projects/' + self.$store.getters.getSelectedProjectCode + '/lastYearEstimates')
          ]).then(axios.spread((geoJsonRes, estimatesRes) => {
            let allSitesGeoJson = geoJsonRes.data;
            let lastYearEstimates = {};
            let siteGroupsGeoJson = {};

            estimatesRes.data.forEach(x => lastYearEstimates[x.trail] = x.estimate);
            self.lastYearEstimates = lastYearEstimates;

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

            Object.entries(siteGroupsGeoJson).forEach(([, site]) => {
              let siteLayer = L.geoJSON(site, {style: defaultStyle, pointToLayer: self._pointToMarker})
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

              self.visibleLayers.push(siteLayer);
              projectSites[siteLayer.trailName] = siteLayer;
              siteLayer.addTo(this.mapDiv);
            });
            self.$store.dispatch('setProjectSites', projectSites);
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
        this.mapDiv.fitBounds(site.getBounds(), {maxZoom: 10});
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
