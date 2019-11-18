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
        let self = this;
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

        let legend = L.control({position: 'bottomright'});
        legend.onAdd = function () {
          let div = L.DomUtil.create('div', 'info legend');
          let grades = [1, 5, 10, 20, 50, 75, 100];
          // loop through our density intervals and generate a label with a colored square for each interval
          for (let i = 0; i < grades.length; i++) {
            div.innerHTML +=
              '<i style="background:' + self._getColors(grades[i] + 1) + '"></i> ' +
              grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
          }
          return div;
        };
        legend.addTo(mapDiv);

        self.mapDiv = mapDiv;
      },
      _getColors: function(d) {
        return d > 100 ? '#800026' :
          d > 75  ? '#BD0026' :
            d > 50  ? '#E31A1C' :
              d > 20  ? '#FC4E2A' :
                d > 10   ? '#FD8D3C' :
                  d > 5   ? '#FEB24C' :
                    d > 0   ? '#FED976' :
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
            } else if (!self.mapDiv) {
              self._mountMap();
            }
          })

      },
      _addLayersToMap: function () {
        let self = this;
        function layerStyle(layer) {
          return {
            fillColor: self._getColors(layer.properties.visit_days),
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
  @import "../assets/styles/home-locations-map.css";

  #mapHomeLocations {
    height: 74vh;
  }
</style>
