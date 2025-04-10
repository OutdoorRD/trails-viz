<template>
  <div class="chart-container">
    <div id="chart" ref="chart"></div>
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading data...</p>
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import Plotly from 'plotly.js-dist';
  import {VIZ_MODES} from '../store/constants';

  export default {
    name: "HomeLocations",
    data: function () {
      return {
        projectName: null,
        projectCode: null,
        siteid: null,
        homeLocations: null,
        randomSeed: null,
        loading: false
      }
    },
    computed: {
      selectedSource() {
        return this.$store.getters.getSelectedSource;
      },
      yearRange() {
        return this.$store.getters.getYearRange;
      }
    },
    watch: {
      selectedSource() {
        this.renderTreeMap();
      },
      yearRange() {
        this.renderTreeMap();
      }
    },
    methods: {
      _randomNumber: function () {
        let x = Math.sin(this.randomSeed += 1) * 10000;
        return x - Math.floor(x);
      },
      _getRandomColor: function () {
        let letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
          color += letters[Math.floor(this._randomNumber() * 16)];
        }
        return color;
      },
      _checkLabelAndAppend: function (labels, name, parentName) {
        if (labels.includes(name)) {
          return name + ' (' + parentName + ')'
        }
        return name
      },
      _mergeTrees: function (x, y) {
        let mergedTree = Object.assign({}, x);
        mergedTree['visit_days'] += y['visit_days'];
        mergedTree['visitors_unq'] += y['visitors_unq'];

        let findCountry = function (countries, name) {
          for (let c of countries) {
            if (c['name'] === name) {
              return c
            }
          }
          return null;
        };

        let findState = function (states, name) {
          for (let s of states) {
            if (s['name'] === name) {
              return s
            }
          }
          return null;
        };

        let findCounty = function (counties, name) {
          for (let c of counties) {
            if (c['name'] === name) {
              return c
            }
          }
          return null;
        };

        for (let country of y['countries']) {
          let mergedTreeCountry = findCountry(mergedTree['countries'], country['name']);
          if (mergedTreeCountry == null) {
            mergedTreeCountry = {'name': country['name'], 'visit_days': 0, 'visitors_unq': 0};
            mergedTree['countries'].push(mergedTreeCountry)
          }
          mergedTreeCountry['visit_days'] += country['visit_days'];
          mergedTreeCountry['visitors_unq'] += country['visitors_unq'];

          if (typeof country['states'] === 'undefined') {
            country['states'] = []
          }
          if (typeof mergedTree['states'] === 'undefined') {
            mergedTree['states'] = []
          }

          for (let state of country['states']) {
            let mergedTreeState = findState(mergedTreeCountry['states'], state['name']);
            if (mergedTreeState == null) {
              mergedTreeState = {'name': state['name'], 'visit_days': 0, 'visitors_unq': 0};
              mergedTreeCountry['states'].push(mergedTreeState)
            }
            mergedTreeState['visit_days'] += state['visit_days'];
            mergedTreeState['visitors_unq'] += state['visitors_unq'];

            if (typeof state['counties'] === 'undefined') {
              state['counties'] = []
            }
            if (typeof mergedTreeState['counties'] === 'undefined') {
              mergedTreeState['counties'] = []
            }

            for (let county of state['counties']) {
              let mergedTreeCounty = findCounty(mergedTreeState['counties'], county['name']);
              if (mergedTreeCounty == null) {
                mergedTreeCounty = {'name': county['name'], 'visit_days': 0, 'visitors_unq': 0};
                mergedTreeState['counties'].push(mergedTreeCounty)
              }
              mergedTreeCounty['visit_days'] += county['visit_days'];
              mergedTreeCounty['visitors_unq'] += county['visitors_unq'];
            }
          }
        }
        return mergedTree
      },
      renderTreeMap: function () {
        this.loading = true;
        // Initialize at this seed
        this.randomSeed = 12;
        let self = this;

        self.clear();

        self.projectName = self.$store.getters.getSelectedProjectName;
        self.projectCode = self.$store.getters.getSelectedProjectCode;
        self.siteid = self.$store.getters.getSelectedSite['siteid'];

        let homeLocationsUrl;
        if (self.$store.getters.getVizMode === VIZ_MODES.PROJECT) {
          homeLocationsUrl = this.$apiEndpoint + '/projects/' + self.projectCode + '/source/' + this.selectedSource + '/homeLocations'
        } else if (self.$store.getters.getVizMode === VIZ_MODES.SITE) {
          homeLocationsUrl = this.$apiEndpoint + '/sites/' + self.siteid + '/source/' + this.selectedSource + '/homeLocations'
        }

        const yearRange = this.$store.getters.getYearRange;
        if (yearRange && yearRange.length === 2) {
          const yearStart = yearRange[0];
          const yearEnd = yearRange[1];
          homeLocationsUrl += `?year_start=${yearStart}&year_end=${yearEnd}`;
        }
        axios.get(homeLocationsUrl)
          .then(response => {
            self.homeLocations = response.data;
            self._renderTreeMap();
          })
          .finally(() => {
            self.loading = false;
          });
      },
      _renderTreeMap: function() {
        let self = this;
        let data = self.homeLocations;
        let labels = [];
        let parents = [];
        let values = [];
        let colors = [];
        let worldLabel = 'World (' + data['visit_days'] + ' Visit Days)';
        let usLabel = 'USA (' + data['visit_days'] + ' Visit Days)';
        let topLabel = (self.selectedSource === 'flickr') ? worldLabel : usLabel;
        labels.push(topLabel);
        values.push(data['visit_days']);
        parents.push('');
        colors.push(this._getRandomColor());
        for (let country of data['countries']) {
          let countryName = country['name'];
          labels.push(countryName);
          values.push(country['visit_days']);
          parents.push(topLabel);
          colors.push(this._getRandomColor());

          for (let state of country['states']) {
            let stateName = this._checkLabelAndAppend(labels, state['name'], country['name']);
            labels.push(stateName);
            values.push(state['visit_days']);
            parents.push(countryName);
            colors.push(this._getRandomColor());

            for (let county of state['counties']) {
              let countyName = this._checkLabelAndAppend(labels, county['name'], state['name']);
              labels.push(countyName);
              values.push(county['visit_days']);
              parents.push(stateName);
              colors.push(this._getRandomColor());
            }
          }
        }
        const vh = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
        const hw = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
        let layout = {
          autosize: false,
          height: Math.floor(0.72 * vh),
          width: Math.floor(0.48 * hw),
          margin: {
            l: 10,
            r: 0,
            b: 0,
            t: 0,
            pad: 0
          }
        };
        Plotly.newPlot('chart',  [{
          type: "treemap",
          labels: labels,
          parents: parents,
          values: values,
          textinfo: 'label+percent root',
          pathbar: {"visible": true},
          branchvalues: "total",
          marker: {
            line: {width: 0.5}
          },
          tiling: {packing : "squarify"}
        }], layout);
      },
      clear: function () {
        this.homeLocations = '';
      }
    }
  }
</script>

<style scoped>

  .chart-container {
    position: relative;
    height: 72vh;
  }


  #chart {
    height: 72vh;
    width: 100%;
    max-width: 100%;
  }
</style>
