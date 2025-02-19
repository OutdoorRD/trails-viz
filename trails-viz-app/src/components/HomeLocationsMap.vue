<template>
  <div id="mapHomeLocations" ref="mapHomeLocations"></div>
</template>

<script>

  import L from "leaflet";
  import axios from "axios";
  import {MAPBOX_CONSTS, VIZ_MODES} from "../store/constants"

  export default {
    name: "HomeLocationsMap",
    props: ["selectedSource"],
    data: function () {
      return {
        mapDiv: '',
        homeLocationsGeoJson: '',
        visibleLayer: '',
        projectCode: '',
        siteid: '',
        clickedState: '',
        clickedCounty: '',
        level: 'state',  // allowed values are ['state', 'county', 'censusTract']
        activated: false
      }
    },
    watch: {
      selectedSource() {
        this.renderHomeLocationsMap();
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
          id: 'mapbox/light-v10',
          accessToken: MAPBOX_CONSTS.TOKEN
        }).addTo(mapDiv);

        let legend = L.control({position: 'bottomright'});
        legend.onAdd = function () {
          let div = L.DomUtil.create('div', 'info legend');
          let grades = [1, 5, 10, 20, 50, 75, 100];
          // loop through our density intervals and generate a label with a colored square for each interval
          div.innerHTML += '<div>Visit Days</div>';
          for (let i = 0; i < grades.length; i++) {
            div.innerHTML +=
              '<i style="background:' + self._getColors(grades[i] + 1) + '"></i> ' +
              grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
          }
          return div;
        };
        legend.addTo(mapDiv);

        let switchOptions = L.control({position: 'topright'});

        switchOptions.onAdd = function() {
          let div = L.DomUtil.create('div');
          div.innerHTML +=
            "<a href='javascript:void(0);' id='backToState' class='hl-switch-options hl-hidden'>Back to State Level</a>" +
            "<a href='javascript:void(0);' id='backToCounty' class='hl-switch-options hl-hidden'>Back to County Level</a>" + 
            "<a href='javascript:void(0);' id='backToZCTA' class='hl-switch-options hl-hidden'>Back to ZCTA Level</a>";

          return div;
        };

        switchOptions.addTo(mapDiv);
        self.mapDiv = mapDiv;

        // add event listeners to switch back to higher level
        document.getElementById('backToState').addEventListener('click', () => self.renderHomeLocationsMap());
        document.getElementById('backToCounty').addEventListener('click', () => self._renderCountyLevel(self.clickedState));
        document.getElementById('backToZCTA').addEventListener('click', () => self._renderZCTALevel(self.clickedState ,self.clickedCounty));
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
        self.level = 'state';
        if (self.$store.getters.getVizMode === VIZ_MODES.PROJECT) {
          self.projectCode = self.$store.getters.getSelectedProjectCode;
          url = self.$apiEndpoint + '/projects/' + self.projectCode + '/source/' + this.selectedSource + '/homeLocationsState';
        } else if (self.$store.getters.getVizMode === VIZ_MODES.SITE) {
          self.siteid = self.$store.getters.getSelectedSite['siteid'];
          url = self.$apiEndpoint + '/sites/' + self.siteid + '/source/' + this.selectedSource + '/homeLocationsState';
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
      _renderCountyLevel: function(stateCode) {
        let self = this;
        let url;
        self.level = 'county';
        if (self.$store.getters.getVizMode === VIZ_MODES.PROJECT) {
          url = self.$apiEndpoint + '/projects/' + self.projectCode + '/source/' + this.selectedSource + '/homeLocationsCounty/' + stateCode;
        } else if (self.$store.getters.getVizMode === VIZ_MODES.SITE) {
          url = self.$apiEndpoint + '/sites/' + self.siteid + '/source/' + this.selectedSource + '/homeLocationsCounty/' + stateCode;
        }
        axios.get(url)
          .then(response => {
            self.homeLocationsGeoJson = response.data;
            self._addLayersToMap();
          })
      },
      _renderZCTALevel: function(stateCode, countyCode) {
        let self = this;
        let url;
        self.level = 'zcta';
        if (self.$store.getters.getVizMode === VIZ_MODES.PROJECT) {
          url = self.$apiEndpoint + '/projects/' + self.projectCode + '/source/' + this.selectedSource + '/homeLocationsZCTA/' + stateCode + '/' + countyCode;
        } else if (self.$store.getters.getVizMode === VIZ_MODES.SITE) {
          url = self.$apiEndpoint + '/sites/' + self.siteid + '/source/' + this.selectedSource + '/homeLocationsZCTA/' + stateCode + '/' + countyCode;
        }
        axios.get(url)
          .then(response => {
            self.homeLocationsGeoJson = response.data;
            self._addLayersToMap();
          })
      },
      _renderCensusTractLevel: function(stateCode, countyCode) {
        let self = this;
        let url;
        self.level = 'censusTract';
        if (self.$store.getters.getVizMode === VIZ_MODES.PROJECT) {
          url = self.$apiEndpoint + '/projects/' + self.projectCode + '/homeLocationsCensusTract/' + stateCode + '/' + countyCode;
        } else if (self.$store.getters.getVizMode === VIZ_MODES.SITE) {
          url = self.$apiEndpoint + '/sites/' + self.siteid + '/homeLocationsCensusTract/' + stateCode + '/' + countyCode;
        }
        axios.get(url)
          .then(response => {
            self.homeLocationsGeoJson = response.data;
            self._addLayersToMap();
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

        if (self.level === 'state') {
          document.getElementById('backToState').classList.add('hl-hidden');
          document.getElementById('backToCounty').classList.add('hl-hidden');
          document.getElementById('backToZCTA').classList.add('hl-hidden');
        } 
        else if (self.level === 'county') {
          document.getElementById('backToState').classList.remove('hl-hidden');
          document.getElementById('backToCounty').classList.add('hl-hidden');
          document.getElementById('backToZCTA').classList.add('hl-hidden');
        }
        else if (self.level === 'zcta') {
          document.getElementById('backToState').classList.add('hl-hidden');
          document.getElementById('backToCounty').classList.remove('hl-hidden');
          document.getElementById('backToZCTA').classList.add('hl-hidden');
        } 
        else if (self.level === 'censusTract') {
          document.getElementById('backToCounty').classList.add('hl-hidden');
          document.getElementById('backToState').classList.add('hl-hidden');
          document.getElementById('backToZCTA').classList.remove('hl-hidden');
        }

        function getTooltipHtml(layer) {
          let props = layer.feature.properties;
          let toolTip = '<table class="home-location-tooltip">';

          if (props.state) {
            toolTip += '<tr><td> State </td><td>' + props.state + '</td></tr>';
          }
          if (props.county) {
            toolTip += '<tr><td> County</td><td>' + props.county + '</td></tr>';
          }

          toolTip += '<tr><td> Visit Days</td><td>' + props.visit_days + '</td></tr>' +
            '<tr><td> Unique Visitors</td><td>' + props.visitors_unq + '</td></tr>';

          if (props.population) {
            toolTip += '<tr><td> Total Population</td><td>' + props.population + '</td></tr>';
          }
          if (props.median_income) {
            toolTip += '<tr><td> Median Income</td><td>' + props.median_income + '</td></tr>';
          }
          if (props.housing_cost_burden) {
            toolTip += '<tr><td> Housing Cost Burden</td><td>' + props.housing_cost_burden + '</td></tr>';
          }
          if (props.minority_percentage) {
            toolTip += '<tr><td> Percent Minority</td><td>' + props.minority_percentage + '</td></tr>';
          }
          if (props.svi) {
            toolTip += '<tr><td> Social Vulnerability Index</td><td>' + parseFloat(Math.round(props.svi * 100)/ 100).toFixed(2) + '</td></tr>';
          }

          toolTip += '</table>';
          return toolTip;
        }

        if (self.visibleLayer) {
          self.mapDiv.removeLayer(self.visibleLayer);
        }

        self.visibleLayer = L.geoJSON(self.homeLocationsGeoJson, {style: layerStyle})
          .bindTooltip(layer => getTooltipHtml(layer))
          .on('click', event => {
            const props = event.layer.feature.properties;
            const stateCode = props['state_code'];
            if (self.level === 'state') {
              self._renderCountyLevel(stateCode);
              self.clickedState = stateCode;
            }
            else if (self.level === 'county') {
              const countyCode = props['county_code'];
              // self._renderCensusTractLevel(stateCode, countyCode);
              self._renderZCTALevel(stateCode, countyCode);
              self.clickedState = stateCode;
              self.clickedCounty = countyCode;
            }
            else if (self.level === 'zcta') {
              const countyCode = props['county_code'];
              self._renderCensusTractLevel(stateCode, countyCode);
              self.clickedState = stateCode;
              self.clickedCounty = countyCode;
            }
          });
        self.visibleLayer.addTo(self.mapDiv);

        // on state level we only want to show main land US i.e. exclude Alaska, Hawaii etc.
        // But those states will be on map and users can navigate to that location
        const excludedStateCodes = ['02', '15'];
        let mainLandLocations = self.homeLocationsGeoJson.features.filter(x => !excludedStateCodes.includes(x['properties']['state_code']));
        mainLandLocations = {'type': 'FeatureCollection', 'features': mainLandLocations};
        let mainLandLayer = L.geoJSON(mainLandLocations);   // This layer will never be visible

        self.mapDiv.fitBounds(mainLandLayer.getBounds());
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
    height: 72vh;
  }
</style>
