<template>
  <div id="chart" ref="chart"></div>
</template>

<script>
  import {store} from "../store";
  import Plotly from 'plotly.js-dist';

  export default {
    name: "HomeLocations",
    data: function () {
      return {
        homeLocations: null,
        randomSeed: null,
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
          return name + '(' + parentName + ')'
        }
        return name
      },
      renderTreeMap: function () {
        // Initialize at this seed
        this.randomSeed = 12;
        let self = this;
        self.homeLocations = store.homeLocations;
        let data = self.homeLocations;
        let labels = [];
        let parents = [];
        let values = [];
        let colors = [];
        labels.push('World');
        values.push(data['visit_days']);
        parents.push('');
        colors.push(this._getRandomColor());
        for (let country of data['countries']) {
          labels.push(country['name']);
          values.push(country['visit_days']);
          parents.push('World');
          colors.push(this._getRandomColor());

          for (let state of country['states']) {
            labels.push(this._checkLabelAndAppend(labels, state['name'], country['name']));
            values.push(state['visit_days']);
            parents.push(country['name']);
            colors.push(this._getRandomColor());

            for (let county of state['counties']) {
              labels.push(this._checkLabelAndAppend(labels, county['name'], state['name']));
              values.push(county['visit_days']);
              parents.push(state['name']);
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
