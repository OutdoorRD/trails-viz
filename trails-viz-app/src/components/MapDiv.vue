<template>
  <div>
    <b-alert :show="dismissCountDown" dismissible fade variant="warning" @dismiss-count-down="countDownChanged">
      Only two sites can be compared at a time!
    </b-alert>
    <!-- Range Slider for Year Selection -->
    
      <v-app>
        <div 
          v-if="showChatbotMapCondition"
          class="range-slider-container"
        >
          <v-card 
            style="
              max-width: 100%; 
              max-height: 100%; 
              padding: 0px; 
              margin: 0; 
              display: flex;
              flex-direction: column;
              align-items: center; 
              justify-content: flex-start;
            ">
            <v-card-text style="width: 100%; padding-top: 4px;">
              <v-range-slider
                v-if="yearRange && minYear !== undefined && maxYear !== undefined"
                v-model="yearRange"
                :min="minYear"
                :max="maxYear"
                ticks="always"
                tick-size = 4
                thumb-label
                @change="onYearRangeChange"
              >
                <template v-slot:prepend>
                  <span>{{ minYear }}</span>
                </template>
                <template v-slot:append>
                  <span>{{ maxYear }}</span>
                </template>
              </v-range-slider>
            </v-card-text>
          </v-card>
        </div>
        
        <div class="map-div" ref="mapDiv"></div>
      </v-app>
  </div>
</template>


<script>
  import L from "leaflet";
  import axios from "axios";
  import {MAPBOX_CONSTS} from "../store/constants";
  import {EventBus} from "../event-bus";
  import * as turf from "@turf/turf";
  import { TAB_CONFIG } from "../store/constants";

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
    weight: 0.8,
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
    fillOpacity: 0.8
  };

  const circleMarkerDefaultStyle = {
    color: "#3388ff", // Border color
    weight: 1, // Border width
    fillColor: "#3388ff", // Fill color
    fillOpacity: 0.8, // Transparency
  }

  const highlightStyle = {
    color: "#8A00C4",
    weight: 0.8,
    fillColor: '#8A00C4',
    fillOpacity: 0.8
  };


  export default {
    name: "MapDiv",
    props: {
      activeSubTab: {
        type: String,
        required: true,
      },
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
        // chatbotSitesLayer : [],
        chatbotActivityLayer : [],
        lastYearEstimates: undefined,
        chatbotResponseCounts: undefined,
        chatbotResData: undefined,
        yearRange: [], // Default range
        minYear: undefined,
        maxYear: undefined,
        trailNamesInDropdown: [],
      }
    },
    computed: {
      showChatbotMapCondition() {
        return this.visibleTabGroup === 'visitorCharacteristics' && 
               TAB_CONFIG.chatbotMapTabs.includes(this.activeSubTab) && 
               this.chatbotResData.length > 0;
      }
    },
    watch: {
      activeSubTab() {
        this.onSubTabChange();
      },
      visibleTabGroup(newTabGroup) {
        this.onTabGroupChange(newTabGroup);
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
      EventBus.$on('top-bar:site-search-results', self.searchSite); // David over here
    },
    beforeDestroy() {
      let self = this;
      EventBus.$off('top-bar:site-selected', self.selectSite);
      EventBus.$off('top-bar:site-search-results', self.searchSite); // David over here
    },
    methods: {
      onYearRangeChange() {
        this.chatbotResponseCounts = this.filterChatbotData();
        this.updateChatbotActivityLayer();
      },
      onTabGroupChange(newTabGroup) {
        if (newTabGroup !== 'visitorCharacteristics') {
          this.showBasicMap();
        }
        else {
          this.onSubTabChange()
        }
      },
      onSubTabChange() {
        if (this.showChatbotMapCondition) {
          this.showChatbotMap()
        } 
        else {
          this.showBasicMap()
        }
      },
      showChatbotMap() {
          this.addChatbotActivityLayer()
          this.changeToChatbotSitesLayer()
      },
      showBasicMap() {
        this.removeChatbotActivityLayer()
        this.changeToBasicSitesLayer()
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
          ...circleMarkerDefaultStyle,
        })//.bindTooltip(`${feature.properties.name}: ${data}`);
      },


      renderProjectSites: function () {
        let self = this;
        let projectSites = {};
        let centroidFeatures = [];

        this.createPanes();

        // remove the existing visible sites of the project
        // self.chatbotSitesLayer.forEach(siteLayer => this.mapDiv.removeLayer(siteLayer));
        self.basicSitesLayer.forEach(siteLayer => this.mapDiv.removeLayer(siteLayer));
        self.chatbotActivityLayer.forEach(siteLayer => this.mapDiv.removeLayer(siteLayer))

        const requests = [
          axios.get(self.$apiEndpoint + '/projects/' + self.$store.getters.getSelectedProjectCode + '/sites/geojson')
        ];

        // Conditionally include the last two endpoints based on user status
        const userRole = this.$store.getters.getUserRole;
        // console.log('User Role:', userRole);
        if (userRole === 'admin' || userRole === 'manager') {
          requests.push(
            // axios.get(self.$apiEndpoint + '/projects/' + self.$store.getters.getSelectedProjectCode + '/lastYearEstimates'),
            axios.get(self.$apiEndpoint + '/projects/' + self.$store.getters.getSelectedProjectCode + '/get_annual_chatbot_response_counts')
          );
        }
        axios
        .all(requests)
        .then(
            axios.spread((geoJsonRes, chatbotRes) => {
            // console.log('HI DAVID')
            // console.log('user role:',this.$store.getters.getUserRole)
            const allSitesGeoJson = geoJsonRes.data;
            this.mapDiv.fitBounds(L.geoJson(allSitesGeoJson).getBounds());
            let siteGroupsGeoJson = self.groupGeoJsonBySite(allSitesGeoJson);
            self.addBasicSitesLayer(siteGroupsGeoJson, projectSites); // Add basic sites layer logic
            this.chatbotResData = chatbotRes.data
            if (userRole === 'admin' || userRole === 'manager' && this.chatbotResData.length > 0) {
              // console.log('this.chatbotResData:', this.chatbotResData)
              self.processYearRange(chatbotRes.data);
              self.chatbotResponseCounts = self.filterChatbotData();
              self.initializeChatbotActivityLayer(siteGroupsGeoJson);
              this.onSubTabChange()
            }
            self.$store.dispatch('setProjectSites', projectSites);
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
        // console.log("Calculated Year Range:", this.yearRange);
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
        // console.log(geoJsonData)
        let siteGroupsGeoJson = {};
        const selectedProjectCode = this.$store.getters.getSelectedProjectCode;
        // console.log('selectedProjectCode', selectedProjectCode)
        geoJsonData.features.forEach((feature) => {
          const siteid = feature.properties.siteid;
          const trailName = feature.properties.Trail_name;
          const prjctCode = feature.properties.Prjct_code;
          const prjctCodeList = prjctCode.split(',').map(code => code.trim());
          // if (prjctCodeList.includes(selectedProjectCode)) {
            if (!(siteid in siteGroupsGeoJson)) {
              // console.log('trailName:', trailName, 'siteid:', siteid, 'prjctCode:', prjctCode)
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
        // console.log('siteGroupsGeoJson:', siteGroupsGeoJson)
        return siteGroupsGeoJson;
      },
      // createChatbotAcitivityLayer: function (centroidFeatures) {
      //   const centroidLayer = L.geoJSON(
      //     { type: "FeatureCollection", features: centroidFeatures },
      //     { pointToLayer: this.createCircleMarker }
      //   ).bindTooltip((layer) => layer.feature.properties.name);
      //   this.chatbotActivityLayer.push(centroidLayer);
      // },
      // Change to chatbot sites
      changeToChatbotSitesLayer: function () {
        const selectedSite = this.$store.getters.getSelectedSite;
        const comparingSite = this.$store.getters.getComparingSite;

        this.basicSitesLayer.forEach((site) => {
          // Check if the site is the selected site or the comparing site
          if (site === selectedSite || site === comparingSite) {
            if (selectedSite && comparingSite) {
              site.setStyle(compareStyle); // Keep comparing site styled
            } else {
              site.setStyle(selectedStyle); // Keep selected site styled
            }
          } else {
            const estimate = this.chatbotResponseCounts[site.siteid] || 0;
            const style = estimate === 0 ? solidGreyStyle : solidDefaultStyle;
            site.setStyle(style);
          }
        });
        // let sites = this.$store.getters.getProjectSites;
        // const selectedSite = this.$store.getters.getSelectedSite;
        // const comparingSite = this.$store.getters.getComparingSite;

        // Object.values(sites).forEach((site) => {
        //   // Check if the site is the selected site or the comparing site
        //   if (site === selectedSite || site === comparingSite) {
        //     if (selectedSite && comparingSite) {
        //       site.setStyle(compareStyle); // Keep comparing site styled
        //     }
        //     else {
        //       site.setStyle(selectedStyle); // Keep selected site styled
        //     }
        //   } 
        //   else {
        //     const estimate = this.chatbotResponseCounts[site.siteid] || 0;
        //     const style = estimate === 0 ? solidGreyStyle : solidDefaultStyle;
        //     site.setStyle(style);
        //   }
        // });
      },
      // Change to basic sites
      changeToBasicSitesLayer: function () {
        const selectedSite = this.$store.getters.getSelectedSite;
        const comparingSite = this.$store.getters.getComparingSite;

        this.basicSitesLayer.forEach((site) => {
          // Check if the site is the selected site or the comparing site
          if (site === selectedSite || site === comparingSite) {
            if (selectedSite && comparingSite) {
              site.setStyle(compareStyle); // Keep comparing site styled
            } else {
              site.setStyle(selectedStyle); // Keep selected site styled
            }
          } else {
            site.setStyle(defaultStyle); // Reset others to default style;
          }
        });

        // let sites = this.$store.getters.getProjectSites;
        // const selectedSite = this.$store.getters.getSelectedSite;
        // const comparingSite = this.$store.getters.getComparingSite;

        // Object.values(sites).forEach((site) => {
        //   // Check if the site is the selected site or the comparing site
        //   if (site === selectedSite || site === comparingSite) {
        //     if (selectedSite && comparingSite) {
        //       site.setStyle(compareStyle); // Keep comparing site styled
        //     }
        //     else {
        //       site.setStyle(selectedStyle); // Keep selected site styled
        //     }
        //   } 
        //   else {
        //     site.setStyle(defaultStyle); // Reset others to default style
        //   }
        // });
      },
      // Add basic sites layer
      addBasicSitesLayer: function (siteGroupsGeoJson, projectSites) {
        // console.log('siteGroupsGeoJson',siteGroupsGeoJson)
        Object.entries(siteGroupsGeoJson).forEach(([, site]) => {
          let siteLayer = L.geoJSON(site, {
            pane: "basicSitesPane",
            style: defaultStyle,
          })
            .bindTooltip(site.name)
            .on("mouseover", this.handleMouseOver)
            .on("mouseout", this.handleMouseOut)
            .on("click", this.handleClick);

          siteLayer.siteid = site.siteid;
          siteLayer.trailName = site.name;

          const isDuplicate = Object.values(siteGroupsGeoJson).filter(
            s => s.name === site.name
          ).length > 1;
          siteLayer.trailName = isDuplicate ? `${site.name} (${site.siteid})` : site.name;
          projectSites[siteLayer.siteid] = siteLayer;
          this.basicSitesLayer.push(siteLayer);
          siteLayer.addTo(this.mapDiv)
        });
      },
      initializeChatbotActivityLayer: function (siteGroupsGeoJson) {
        const uniqueTrailNames = new Set();
        Object.entries(siteGroupsGeoJson).forEach(([, site]) => {
          // Calculate the centroid for each site
          const centroid = turf.centroid(site);
          // console.log('Centroid GeoJSON:', centroid);
          centroid.properties = {
            siteid: site.siteid,
            // name: site.name,
          };
          let siteLayer = L.geoJSON(centroid, {
            pane: "circlesPane",
            pointToLayer: this.createCircleMarker,
          })//.bindTooltip(site.name);

          // Assign properties to the layer
          siteLayer.siteid = site.siteid;
          siteLayer.trailName = site.name;
          if (uniqueTrailNames.has(siteLayer.trailName)) {
            siteLayer.trailName = `${site.name} (${site.siteid})`;
          }
          uniqueTrailNames.add(siteLayer.trailName)
          this.chatbotActivityLayer.push(siteLayer);
          // siteLayer.addTo(this.mapDiv);
        });
      },
      addChatbotActivityLayer: function() {
        this.chatbotActivityLayer.forEach((layer) => {
          if (!this.mapDiv.hasLayer(layer)) {
            layer.addTo(this.mapDiv)
          }
        })
      },
      updateChatbotActivityLayer: function() {
        this.chatbotActivityLayer.forEach((layer) => {
          if (layer.eachLayer) {
            layer.eachLayer((circleMarker) => {
              if (circleMarker instanceof L.CircleMarker) {
                const siteid = circleMarker.feature.properties.siteid;
                const data = this.chatbotResponseCounts[siteid] || 0;
                const radius = Math.sqrt(data) * 2;
                circleMarker.setRadius(radius);
              }
            });
          }
        });
      },
      removeChatbotActivityLayer: function() {
        this.chatbotActivityLayer.forEach((layer) => {
          if (this.mapDiv.hasLayer(layer)) {
            this.mapDiv.removeLayer(layer)
          }
        })
      },
      // Mouse event handlers
      handleMouseOver: function (event) {
        if (
          event.target !== this.$store.getters.getSelectedSite &&
          event.target !== this.$store.getters.getComparingSite
        ) {
          event.target.setStyle(hoverStyle);
          const siteid = event.target.siteid;
          const circleMarker = this.chatbotActivityLayer.find(
            (layer) => layer.siteid === siteid
          );
          if (circleMarker) {
            circleMarker.setStyle({
              ...hoverStyle
            });
          }
        }
      },
      handleMouseOut: function (event) {
        if (
            event.target !== this.$store.getters.getSelectedSite &&
            event.target !== this.$store.getters.getComparingSite
          ) {
            this.resetStyle([event.target])
          // let style = defaultStyle
          // if (this.showChatbotMapCondition) {
          //   const estimate =
          //     this.chatbotResponseCounts[event.target.siteid] || 0;
          //     style = estimate === 0 ? solidGreyStyle : solidDefaultStyle
          // }
          // event.target.setStyle(style);
          // const siteid = event.target.siteid;
          // const circleMarker = this.chatbotActivityLayer.find(
          //   (layer) => layer.siteid === siteid
          // );
          // if (circleMarker) {
          //   circleMarker.setStyle({
          //     ...circleMarkerDefaultStyle
          //   });
          // }
        }
      }
      ,
      handleClick: function (event) {
        if (event.originalEvent.ctrlKey) {
          if (
            this.$store.getters.getComparingSite &&
            this.$store.getters.getSelectedSite
          ) {
            this.showAlert();
          } else if (this.$store.getters.getSelectedSite) {
            // console.log('TWO SELECTED')
            this.$store.dispatch("setComparingSite", event.target);
            // console.log(this.$store.getters.getSelectedSite)
            // console.log(this.$store.getters.getComparingSite)
            this.$store.getters.getSelectedSite.setStyle(compareStyle);
            this.$store.getters.getComparingSite.setStyle(compareStyle);
            EventBus.$emit("map-div:compare-activated");
          }
        } else {
          this.selectSite(event.target);
        }
      },
      selectSite: function (target) {
        console.log('Target:',target)
        const trailName = target.trailName
        const siteID = target.siteid
        let self = this;
        if (self.$store.getters.getComparingSite) {
          this.resetStyle([self.$store.getters.getComparingSite])
          // let style = defaultStyle
          // if (this.showChatbotMapCondition) {
          //   console.log('DOES THIS RUN AS WELL??')
          //   const estimate =
          //     this.chatbotResponseCounts[self.$store.getters.getComparingSite.siteid] || 0;
          //     style = estimate === 0 ? solidGreyStyle : solidDefaultStyle
          // }
          // const siteid = self.$store.getters.getComparingSite.siteid;
          // const circleMarker = this.chatbotActivityLayer.find(
          //   (layer) => layer.siteid === siteid
          // );
          // if (circleMarker) {
          //   circleMarker.setStyle({
          //     ...circleMarkerDefaultStyle
          //   });
          // }
          // self.$store.getters.getComparingSite.setStyle(style);
          self.$store.dispatch('setComparingSite', '');
        }
        if (self.$store.getters.getSelectedSite) {
          this.resetStyle([self.$store.getters.getSelectedSite])
          // let style = defaultStyle
          // if (this.showChatbotMapCondition) {
          //   const estimate =
          //     this.chatbotResponseCounts[self.$store.getters.getSelectedSite.siteid] || 0;
          //     style = estimate === 0 ? solidGreyStyle : solidDefaultStyle
          // }
          // const siteid = self.$store.getters.getSelectedSite.siteid;
          // const circleMarker = this.chatbotActivityLayer.find(
          //   (layer) => layer.siteid === siteid
          // );
          // if (circleMarker) {
          //   circleMarker.setStyle({
          //     ...circleMarkerDefaultStyle
          //   });
          // }
          // self.$store.getters.getSelectedSite.setStyle(style);
        }
        // console.log('trailName:', trailName)
        console.log('getProjectSites:',self.$store.getters.getProjectSites);
        // let site = self.$store.getters.getProjectSites[trailName];
        // let site = this.basicSitesLayer.find((layer) => layer.trailName === trailName);
        console.log(this.basicSitesLayer)
        let site = this.basicSitesLayer.find((layer) => layer.siteid === siteID);


        // console.log('selectSite:', site)
        site.setStyle(selectedStyle);
        self.$store.dispatch('setSelectedSite', site);
        EventBus.$emit('map-div:site-selected');
        this.mapDiv.fitBounds(site.getBounds(), {maxZoom: 11});
        const siteid = site.siteid
        // console.log('siteid:', siteid)
        const circleMarker = this.chatbotActivityLayer.find(
          (layer) => layer.siteid === siteid
        );
        if (circleMarker) {
          // console.log('IM IN')
          circleMarker.setStyle({
            ...selectedStyle
          });
        }
      },
      searchSite: function (trailNamesList) {
        this.trailNamesInDropdown = trailNamesList
        const selectedSite = this.$store.getters.getSelectedSite;
        const comparingSite = this.$store.getters.getComparingSite;
        this.resetStyle(this.basicSitesLayer)
        // check if need to restore comparing sites styles
        if (selectedSite && comparingSite) {
          selectedSite.setStyle(compareStyle)
          comparingSite.setStyle(compareStyle)
        }
        // check if need to restore selected site style
        else if (selectedSite) {
          selectedSite.setStyle(selectedStyle)
        }
        // this.basicSitesLayer.forEach(site => site.setStyle(defaultStyle));
        // console.log('so far so good:', trailNamesList)
        
        const matchingSites = this.basicSitesLayer.filter(site =>
          trailNamesList.includes(site.trailName)
        );
        console.log('matchingSites:', matchingSites)
        matchingSites.forEach(site => {
          console.log('Applying style to site:', site, highlightStyle);
          site.setStyle({
            ...highlightStyle, // Highlight style for matching sites
          });
        });

      },
      resetStyle: function(sitesList) {
        sitesList.forEach(site => {
          let style = defaultStyle;
          if (this.trailNamesInDropdown.includes(site.trailName)) {
            style = highlightStyle;
          }
          else if (this.showChatbotMapCondition) {
            const estimate = this.chatbotResponseCounts[site.siteid] || 0;
            style = estimate === 0 ? solidGreyStyle : solidDefaultStyle;
          }
          const circleMarker = this.chatbotActivityLayer.find(
            layer => layer.siteid === site.siteid
          );
          if (circleMarker) {
            circleMarker.setStyle({
              ...circleMarkerDefaultStyle,
            });
          }
          site.setStyle(style);
        });        
      },
      // selectSite: function (trailName) {
      //   let self = this;
      //   if (self.$store.getters.getComparingSite) {
      //     let style = defaultStyle
      //     if (this.showChatbotMapCondition) {
      //       const estimate =
      //         this.chatbotResponseCounts[self.$store.getters.getComparingSite.siteid] || 0;
      //         style = estimate === 0 ? solidGreyStyle : solidDefaultStyle
      //     }
      //     const siteid = self.$store.getters.getComparingSite.siteid;
      //     const circleMarker = this.chatbotActivityLayer.find(
      //       (layer) => layer.siteid === siteid
      //     );
      //     if (circleMarker) {
      //       circleMarker.setStyle({
      //         ...circleMarkerDefaultStyle
      //       });
      //     }
      //     self.$store.getters.getComparingSite.setStyle(style);
      //     self.$store.dispatch('setComparingSite', '');
      //   }
      //   if (self.$store.getters.getSelectedSite) {
      //     let style = defaultStyle
      //     if (this.showChatbotMapCondition) {
      //       const estimate =
      //         this.chatbotResponseCounts[self.$store.getters.getSelectedSite.siteid] || 0;
      //         style = estimate === 0 ? solidGreyStyle : solidDefaultStyle
      //     }
      //     const siteid = self.$store.getters.getSelectedSite.siteid;
      //     const circleMarker = this.chatbotActivityLayer.find(
      //       (layer) => layer.siteid === siteid
      //     );
      //     if (circleMarker) {
      //       circleMarker.setStyle({
      //         ...circleMarkerDefaultStyle
      //       });
      //     }
      //     self.$store.getters.getSelectedSite.setStyle(style);
      //   }
      //   // console.log('trailName:', trailName)
      //   console.log('getProjectSites:',self.$store.getters.getProjectSites);
      //   // let site = self.$store.getters.getProjectSites[trailName];
      //   let site = this.basicSitesLayer.find((layer) => layer.trailName === trailName);
      //   // console.log('selectSite:', site)
      //   site.setStyle(selectedStyle);
      //   self.$store.dispatch('setSelectedSite', site);
      //   EventBus.$emit('map-div:site-selected');
      //   this.mapDiv.fitBounds(site.getBounds(), {maxZoom: 11});
      //   const siteid = site.siteid
      //   // console.log('siteid:', siteid)
      //   const circleMarker = this.chatbotActivityLayer.find(
      //     (layer) => layer.siteid === siteid
      //   );
      //   if (circleMarker) {
      //     // console.log('IM IN')
      //     circleMarker.setStyle({
      //       ...selectedStyle
      //     });
      //   }
      // },
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
  .range-slider-container {
    position: absolute;
    bottom:16vh;
    left: 1vh;
    z-index: 1000;
    width: 50%;
    height: 4vh;
  }
</style>
