<template>
  <div>
    <b-row no-gutters>
      <b-col sm="6">
        <b-list-group>
          <b-list-group-item class="list-group-item">Total Visit Days <span>{{totalVisitDays}}</span></b-list-group-item>
          <b-list-group-item class="list-group-item">Weighted Median Income <span>${{weightedMedianIncome}}</span></b-list-group-item>
        </b-list-group>
      </b-col>
      <b-col sm="6">
        <b-list-group>
          <b-list-group-item class="list-group-item">Weighted Minority Percentage <span>{{weightedMinorityPercentage}}</span></b-list-group-item>
          <b-list-group-item class="list-group-item">Weighted Social Vulnerability Index <span>{{weightedSVI}}</span></b-list-group-item>
        </b-list-group>
      </b-col>
    </b-row>
    <b-row no-gutters>
      <b-col sm="12">
        <div id="income-chart"></div>
      </b-col>
      <b-col sm="12">
        <div id="svi-chart"></div>
      </b-col>
    </b-row>
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
        projectName: null,
        projectCode: null,
        siteid: null,
        demographicData: null,
        totalPopulation: null,
        totalVisitDays: null,
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

        self.projectName = self.$store.getters.getSelectedProjectName;
        self.projectCode = self.$store.getters.getSelectedProjectCode;
        self.siteid = self.$store.getters.getSelectedSite['siteid'];

        let url;
        if (vizMode === VIZ_MODES.PROJECT) {
          url = self.$apiEndpoint + '/projects/' + self.projectCode + '/homeLocationsDemographics';
        } else if (vizMode === VIZ_MODES.SITE) {
          url = self.$apiEndpoint + '/sites/' + self.siteid + '/homeLocationsDemographics';
        }

        axios.get(url)
          .then(response => {
            self.demographicData = response.data;

            // There is a weired bug in either axios or Vue which changes the last element of the array
            // Thus using toString to make a copy of the array
            let income = self.demographicData.filter(o => this._nanToZero(o['median_income']) > 0);
            let svi = self.demographicData.filter(o => this._nanToZero(o['svi']) > 0);

            self._calculateValues();
            self._makeCharts(income, svi);
          });
      },
      _makeCharts: function (income, svi) {
        let incomeVisitDays = {
          '> 0': 0,
          '> 20000': 0,
          '> 40000': 0,
          '> 60000': 0,
          '> 80000': 0,
          '> 100000': 0
        };

        for (const x of income) {
          if (x['median_income'] > 100000) {
            incomeVisitDays['> 100000'] += x['visit_days']
          } else if (x['median_income'] > 80000) {
            incomeVisitDays['> 80000'] += x['visit_days']
          } else if (x['median_income'] > 60000) {
            incomeVisitDays['> 60000'] += x['visit_days']
          } else if (x['median_income'] > 40000) {
            incomeVisitDays['> 40000'] += x['visit_days']
          } else if (x['median_income'] > 20000) {
            incomeVisitDays['> 20000'] += x['visit_days']
          } else {
            incomeVisitDays['> 0'] += x['visit_days']
          }
        }

        let sviVisitDays = {
          '> 0': 0,
          '> 0.2': 0,
          '> 0.4': 0,
          '> 0.6': 0,
          '> 0.8': 0
        };

        for (const x of svi) {
          if (x['svi'] > 0.8) {
            sviVisitDays['> 0.8'] += x['visit_days']
          } else if (x['svi'] > 0.6) {
            sviVisitDays['> 0.6'] += x['visit_days']
          } else if (x['svi'] > 0.4) {
            sviVisitDays['> 0.4'] += x['visit_days']
          } else if (x['svi'] > 0.2) {
            sviVisitDays['> 0.2'] += x['visit_days']
          } else {
            sviVisitDays['> 0'] += x['visit_days']
          }
        }

        this._makeBarChart(incomeVisitDays, '#income-chart', 'Income');
        this._makeBarChart(sviVisitDays, '#svi-chart', 'Social Vulnerability Index');

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
        self.totalVisitDays = totalVisitDays;
        self.weightedMedianIncome = self._nDecimalPlaces(income / totalVisitDays, 0);
        self.weightedMinorityPercentage = self._nDecimalPlaces(minorityPercentage / totalVisitDays, 2);
        self.weightedSVI = self._nDecimalPlaces(svi / totalVisitDays, 3);
      },
      _makeBarChart: function (data, htmlElemId, title) {
        let categories = Object.keys(data);
        let values = Object.values(data);
        values.unshift('Visit Days');

        // now create a bar chart using the data
        c3.generate({
          bindto: htmlElemId,
          size: {
            height: 200
          },
          axis: {
            x: {
              type: 'category',
              categories: categories,
              label: {
                text: title,
                position: 'outer-center'
              },
              tick: {
                multiline: false
              },
              height: 40
            },
            y: {
              label: {
                text: 'Visit Days',
                position: 'outer-middle'
              }
            }
          },
          legend: {
            show: false
          },
          data: {
            columns: [values],
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
    padding-right: 15px;
    font-weight: bold;
    opacity: 0.7;
  }
</style>
