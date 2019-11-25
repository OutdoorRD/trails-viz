<template>
  <div>
    <b-row no-gutters>
      <b-col>
        <b-list-group>
          <b-list-group-item class="list-group-item">Total Population <span>{{totalPopulation}}</span></b-list-group-item>
          <b-list-group-item class="list-group-item">Weighted Median Income <span>${{weightedMedianIncome}}</span></b-list-group-item>
          <b-list-group-item class="list-group-item">Weighted Minority Percentage <span>{{weightedMinorityPercentage}}</span></b-list-group-item>
          <b-list-group-item class="list-group-item">Weighted Social Vulnerability Index <span>{{weightedSVI}}</span></b-list-group-item>
        </b-list-group>
      </b-col>
    </b-row>
    <b-row no-gutters id="income-chart"></b-row>
    <b-row no-gutters id="svi-chart"></b-row>
  </div>
</template>

<script>
  import c3 from 'c3'
  import axios from 'axios'
  import {VIZ_MODES} from "../store/constants";

  export default {
    name: "DemographicsSummary",
    data: function () {
      return {
        project: null,
        siteid: null,
        demographicData: null,
        totalPopulation: null,
        weightedMedianIncome: null,
        weightedMinorityPercentage: null,
        weightedSVI: null
      }
    },
    methods: {
      _nanToZero: function (x) {
        if (x == null || isNaN(parseFloat(x)) || x < 0) {
          return 0
        }
        return x
      },
      _nDecimalPlaces: function (x, n) {
        if (x == null || isNaN(parseFloat(x))) {
          return 0
        }
        let factor = 10 ** n;
        return parseFloat(Math.round(x * factor) / factor).toFixed(n)
      },
      renderDemographicsSummary: function () {
        let self = this;
        let vizMode = self.$store.getters.getVizMode;

        self.project = self.$store.getters.getSelectedProject;
        self.siteid = self.$store.getters.getSelectedSite['siteid'];

        let url;
        if (vizMode === VIZ_MODES.PROJECT) {
          url = self.$apiEndpoint + '/projects/' + self.project + '/homeLocationsDemographics';
        } else if (vizMode === VIZ_MODES.SITE) {
          url = self.$apiEndpoint + '/sites/' + self.siteid + '/homeLocationsDemographics';
        }

        axios.get(url)
          .then(response => {
            self.demographicData = response.data;

            // There is a weired bug in either axios or Vue which changes the last element of the array
            // Thus using toString to make a copy of the array
            let income = self.demographicData.map(o => this._nanToZero(o['median_income'])).filter(x => x > 0);
            let svi = self.demographicData.map(o => this._nanToZero(o['svi'])).filter(x => x > 0);

            self._calculateValues();
            self._makeCharts(income, svi);
          });
      },
      _makeCharts: function (income, svi) {
        this._makeHistogram(income, '#income-chart', 0, 'Median Income');
        this._makeHistogram(svi, '#svi-chart', 3, 'Social Vulnerability Index');
      },
      _calculateValues: function () {
        let self = this;
        let population = 0, income = 0, minorityPercentage = 0, svi = 0, totalVisitDays = 0;
        for (const t of self.demographicData) {
          const visitDays = self._nanToZero(t['visit_days']);
          population += self._nanToZero(t['population']);
          income += self._nanToZero(t['median_income']) * visitDays;
          minorityPercentage += self._nanToZero(t['minority_percentage']) * visitDays;
          svi += self._nanToZero(t['svi']) * visitDays;
          totalVisitDays += visitDays;
        }

        if (totalVisitDays === 0) {
          totalVisitDays = 1
        }
        self.totalPopulation = population;
        self.weightedMedianIncome = self._nDecimalPlaces(income / totalVisitDays, 0);
        self.weightedMinorityPercentage = self._nDecimalPlaces(minorityPercentage / totalVisitDays, 2);
        self.weightedSVI = self._nDecimalPlaces(svi / totalVisitDays, 3);
      },
      _makeHistogram: function (y, htmlElemId, decimalPlaces, title) {
        let nBins = 20;
        y = y.sort((a, b) => a === b ? 0 : a < b ? -1: 1);
        let n = y.length;

        if (n < nBins) {
          nBins = n;
        }

        let step = (y[n - 1] - y[0]) / nBins;
        let bins = [y[0]];
        for (let i = 0; i < nBins - 1; i += 1) {
          bins.push(bins[i] + step)
        }

        function getBin(x) {
          for (let i = 19; i >= 0; i -= 1) {
            if (x >= bins[i]) {
              return i;
            }
          }
        }

        let counts = new Uint16Array(nBins);
        for (let i = 0; i < n; i += 1) {
          counts[getBin(y[i])] += 1
        }
        let data = ['data'];
        counts.forEach(x => data.push(x));
        bins = bins.map(x => this._nDecimalPlaces(x, decimalPlaces));

        // now create a bar chart using the data
        c3.generate({
          bindto: htmlElemId,
          size: {
            height: 240
          },
          axis: {
            x: {
              type: 'category',
              categories: bins,
              tick: {
                rotate: 60,
                multiline: false
              },
              height: 40
            },
            y: {
              label: {
                text: 'Number of Census Tracts',
                position: 'outer-middle'
              }
            }
          },
          legend: {
            show: false
          },
          data: {
            columns: [data],
            type: 'bar'
          }
        })
      }
    }
  }
</script>

<style scoped>
  .list-group-item {
    padding: 5px 10px 5px 10px;
  }
  .list-group-item span {
    float: right;
    padding-right: 30px;
    font-weight: bold;
    opacity: 0.7;
  }
</style>
