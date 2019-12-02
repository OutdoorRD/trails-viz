<template>
  <div id="chart" ref="chart"></div>
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
        comparingSite: null,
        comparingSiteHomeLocations: null,
        randomSeed: null
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
        // Initialize at this seed
        this.randomSeed = 12;
        let self = this;

        if (self.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
          let comparingSiteId = self.$store.getters.getComparingSite['siteid'];
          self.comparingSite = self.$store.getters.getComparingSite;
          axios.get(self.$apiEndpoint + '/sites/' + comparingSiteId + '/homeLocations')
            .then(response => {
              self.comparingSiteHomeLocations = response.data;
              self._renderTreeMap();
            });
          return
        }

        self.clear();

        self.projectName = self.$store.getters.getSelectedProjectName;
        self.projectCode = self.$store.getters.getSelectedProjectCode;
        self.siteid = self.$store.getters.getSelectedSite['siteid'];

        let homeLocationsUrl;
        if (self.$store.getters.getVizMode === VIZ_MODES.PROJECT) {
          homeLocationsUrl = this.$apiEndpoint + '/projects/' + self.projectCode + '/homeLocations'
        } else if (self.$store.getters.getVizMode === VIZ_MODES.SITE) {
          homeLocationsUrl = self.$apiEndpoint + '/sites/' + self.siteid + '/homeLocations'
        }

        axios.get(homeLocationsUrl)
          .then(response => {
            self.homeLocations = response.data;
            self._renderTreeMap();
          });
      },
      _renderTreeMap: function() {
        let self = this;
        let data = self.homeLocations;
        if (self.$store.getters.getComparingSite) {
          data = self._mergeTrees(self.homeLocations, self.$store.getters.getComparingHomeLocations)
        }
        let labels = [];
        let parents = [];
        let values = [];
        let colors = [];
        let worldLabel = 'World (' + data['visit_days'] + ')';
        labels.push(worldLabel);
        values.push(data['visit_days']);
        parents.push('');
        colors.push(this._getRandomColor());
        for (let country of data['countries']) {
          let countryName = country['name'];
          labels.push(countryName);
          values.push(country['visit_days']);
          parents.push(worldLabel);
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
        let layout = {
          autosize: false,
          height: 400,
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
  #chart {
    height: 500px;
    width: 100%;
    max-width: 100%;
    overflow:auto;
  }
</style>
