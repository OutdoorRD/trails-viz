<template>
  <div class="map-div" ref="mapDiv"></div>
</template>

<script>
  import L from "leaflet";
  import axios from "axios";
  import {store} from "../store";

  // The following two statements are required because of an issue with leaflet and webpack
  // see https://github.com/Leaflet/Leaflet/issues/4968#issuecomment-483402699
  delete L.Icon.Default.prototype._getIconUrl;

  L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
  });

  const MAPBOX_TOKEN = "pk.eyJ1IjoiZGF2ZW1maXNoIiwiYSI6ImNqZnpvZXNtZzU1bXMzMm52M3g0NDg1NjcifQ.vuO6ajviePMVNbQWd4o3TQ";
  const MAPBOX_TILES_API = "https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}";
  const MAPBOX_ATTRIBUTION = '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © ' +
    '<a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
    '<a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a>';

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

  export default {
    name: "MapDiv",
    data: function() {
      return {
        visibleLayers : []
      }
    },
    mounted() {
      const mapDiv = L.map(this.$refs["mapDiv"], {
        center: [40.53, -99.1],
        zoom: 5
      });

      const outdoorLayer = L.tileLayer(MAPBOX_TILES_API, {
        attribution: MAPBOX_ATTRIBUTION,
        maxZoom: 18,
        id: "mapbox.outdoors",
        accessToken: MAPBOX_TOKEN
      });

      const streetsLayer = L.tileLayer(MAPBOX_TILES_API, {
        attribution: MAPBOX_ATTRIBUTION,
        maxZoom: 18,
        id: "mapbox.streets",
        accessToken: MAPBOX_TOKEN
      });

      const satelliteLayer = L.tileLayer(MAPBOX_TILES_API, {
        attribution: MAPBOX_ATTRIBUTION,
        maxZoom: 18,
        id: "mapbox.satellite",
        accessToken: MAPBOX_TOKEN
      });

      L.control.layers({"outdoor": outdoorLayer, "streets": streetsLayer, "satellite": satelliteLayer}).addTo(mapDiv);
      outdoorLayer.addTo(mapDiv);

      this.mapDiv = mapDiv
    },
    methods: {
      renderProjectSites: function () {
        let self = this;

        // remove the existing visible sites of the project
        self.visibleLayers.forEach(siteLayer => this.mapDiv.removeLayer(siteLayer));

        axios
          .get(self.$apiEndpoint + "/sites/geojson?projectGroup=" + store.selectedProject)
          .then(response => {
            let siteGroupsGeoJson = {};
            let allSitesGeoJson = response.data;
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
              let siteLayer = L.geoJSON(site, {style: defaultStyle})
                .bindTooltip(site["name"])
                .on('mouseover', function (event) {
                  if (event.target !== store.selectedSite) {
                    event.target.setStyle(hoverStyle);
                  }
                })
                .on('mouseout', function (event) {
                  if (event.target !== store.selectedSite) {
                    event.target.setStyle(defaultStyle);
                  }
                })
                .on('click', function (event) {
                  self.selectSite(event.target)
                });

              self.visibleLayers.push(siteLayer);
              siteLayer.addTo(this.mapDiv);

              // custom properties can be added to JS objects
              siteLayer.siteid = site["siteid"];
              siteLayer.trailName = site["name"];
            })
        })
      },
      selectSite: function (selectedLayer) {
        if (store.selectedSite) {
          store.selectedSite.setStyle(defaultStyle);
        }
        selectedLayer.setStyle(selectedStyle);
        store.setSelectedSite(selectedLayer);
        this.$emit('site-selected');
      }
    }
  }
</script>

<style scoped>
  @import "~leaflet/dist/leaflet.css";
  .map-div {
    height: 640px;
  }
</style>
