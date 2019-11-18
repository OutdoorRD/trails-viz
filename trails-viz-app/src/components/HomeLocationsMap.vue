<template>
  <div id="mapHomeLocations" ref="mapHomeLocations"></div>
</template>

<script>

  import L from "leaflet";
  import axios from "axios";
  import {MAPBOX_CONSTS, VIZ_MODES} from "../store/constants"

  export default {
    name: "HomeLocationsMap",
    data: function () {
      return {
        mapDiv: '',
        homeLocationsGeoJson: '',
        visibleLayer: '',
        activated: false
      }
    },
    methods: {
      _mountMap: function() {
        const mapDiv = L.map(this.$refs["mapHomeLocations"], {
          center: [40.53, -99.1],
          zoom: 5
        });
        L.tileLayer(MAPBOX_CONSTS.TILES_API, {
          attribution: MAPBOX_CONSTS.ATTRIBUTION,
          maxZoom: 18,
          id: 'mapbox.light',
          accessToken: MAPBOX_CONSTS.TOKEN
        }).addTo(mapDiv);

        this.mapDiv = mapDiv;
      },
      _getColors: function(d) {
        return d > 1000 ? '#800026' :
          d > 500  ? '#BD0026' :
            d > 200  ? '#E31A1C' :
              d > 100  ? '#FC4E2A' :
                d > 50   ? '#FD8D3C' :
                  d > 20   ? '#FEB24C' :
                    d > 10   ? '#FED976' :
                      '#FFEDA0';
      },
      renderHomeLocationsMap: function () {
        let self = this;
        let url;
        if (self.$store.getters.getVizMode === VIZ_MODES.PROJECT) {
          let project = self.$store.getters.getSelectedProject;
          url = self.$apiEndpoint + '/projects/' + project + '/homeLocationsCensusTract';
        } else if (self.$store.getters.getVizMode === VIZ_MODES.SITE) {
          let siteid = self.$store.getters.getSelectedSite['siteid'];
          url = self.$apiEndpoint + '/sites/' + siteid + '/homeLocationsCensusTract';
        }

        axios.get(url)
          .then(response => {
            self.homeLocationsGeoJson = response.data;
            if (self.activated) {
              self._addLayersToMap();
            } else {
              self._mountMap();
            }
          })

      },
      _addLayersToMap: function () {
        let self = this;
        function layerStyle(layer) {
          return {
            fillColor: self._getColors(layer.properties.visit_days * 50),
            weight: 0.5,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7
          };
        }

        if (self.visibleLayer) {
          self.mapDiv.removeLayer(self.visibleLayer);
        }

        self.visibleLayer = L.geoJSON(self.homeLocationsGeoJson, {style: layerStyle})
          .bindTooltip(layer => layer.feature.properties.visit_days.toString());
        self.visibleLayer.addTo(self.mapDiv);
        self.mapDiv.fitBounds(self.visibleLayer.getBounds(), {maxZoom: 9});
      },
      activateHomeLocationsMap: function () {
        let self = this;
        if (!self.activated) {
          self.activated = true;
          setTimeout(() => {
            self.mapDiv.invalidateSize();
            self._addLayersToMap();
          }, 100)
        }
      }
    }
  }

</script>

<style scoped>
  @import "~leaflet/dist/leaflet.css";

  #mapHomeLocations {
    height: 540px;
  }
</style>
