<template>
  <div class="demographics-container">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading data...</p>
    </div>
    <b-row no-gutters>
      <b-col sm="6">
        <b-list-group>
          <b-list-group-item class="list-group-item">Total Visit Days <span class="value">{{totalVisitDays}}</span></b-list-group-item>
          <b-list-group-item class="list-group-item">Average Social Vulnerability Index <span v-b-tooltip.hover
            title="Average vulnerability score of visitors' ZCTA/census tract. Social Vulnerability Index (SVI) uses 16 U.S. Census variables to identify communities vulnerable to stressors. SVI ranges from 0 (least vulnerable) to 1 (most vulnerable)."
            class="info-icon">&#8505;</span>
            <span class="value">{{weightedSVI}}</span>
          </b-list-group-item>
        </b-list-group>
      </b-col>
      <b-col sm="6">
        <b-list-group>
          <b-list-group-item class="list-group-item">Average Percent Minority <span v-b-tooltip.hover
            title="Estimated percent of visit days that are from visitors who are racial and/or ethnic minorities (anything other than non-Hispanic white), based on their home ZIP Code/census tract."
            class="info-icon">&#8505;</span>
            <span class="value">{{weightedMinorityPercentage}}%</span>
          </b-list-group-item>
          <b-list-group-item class="list-group-item">Average Housing Cost Burden <span v-b-tooltip.hover
            title="Estimated percent of visit days that are from visitors who are housing cost-burdened (spend 30% or more of their household income on housing), based on their home ZIP Code/census tract."
            class="info-icon">&#8505;</span>
            <span class="value">{{weightedHousingCostBurdenPercentage}}%</span>
          </b-list-group-item>
        </b-list-group>
      </b-col>
    </b-row>
    <b-row no-gutters>
      <b-col sm="12">
        <div id="housing-cost-burden-chart"></div>
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
        weightedHousingCostBurdenPercentage: null,
        weightedMinorityPercentage: null,
        weightedSVI: null,
        loading: false,
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
        this.renderDemographicsSummary();
      },
      yearRange() {
        this.renderDemographicsSummary();
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
        self.loading = true
        let vizMode = self.$store.getters.getVizMode;

        self.projectName = self.$store.getters.getSelectedProjectName;
        self.projectCode = self.$store.getters.getSelectedProjectCode;
        self.siteid = self.$store.getters.getSelectedSite['siteid'];

        let url;
        if (vizMode === VIZ_MODES.PROJECT) {
          url = self.$apiEndpoint + '/projects/' + self.projectCode + '/source/' + this.selectedSource + '/homeLocationsDemographics';
        } else if (vizMode === VIZ_MODES.SITE) {
          url = self.$apiEndpoint + '/sites/' + self.siteid + '/source/' + this.selectedSource + '/homeLocationsDemographics';
        }

        const yearRange = this.$store.getters.getYearRange;
        if (yearRange && yearRange.length === 2) {
          const yearStart = yearRange[0];
          const yearEnd = yearRange[1];
          url += `?year_start=${yearStart}&year_end=${yearEnd}`;
        }

        axios.get(url)
          .then(response => {
            self.demographicData = response.data;

            // There is a weired bug in either axios or Vue which changes the last element of the array
            // Thus using toString to make a copy of the array
            let housingCostBurdenPercentage = self.demographicData.filter(o => this._nanToZero(o['housing_cost_burden']) > 0);
            let svi = self.demographicData.filter(o => this._nanToZero(o['svi']) > 0);

            self._calculateValues();
            self._makeCharts(housingCostBurdenPercentage, svi);
          })
          .finally(() => {
            this.loading = false
          })
      },
      _makeCharts: function (housingCostBurdenPercentage, svi) {
        let housingCostBurdenVisitDays = {
          '> 0%': 0,
          '> 20%': 0,
          '> 40%': 0,
          '> 60%': 0,
          '> 80%': 0
        };

        for (const x of housingCostBurdenPercentage) {
          if (x['housing_cost_burden'] > 80) {
            housingCostBurdenVisitDays['> 80%'] += x['visit_days']
          } else if (x['housing_cost_burden'] > 60) {
            housingCostBurdenVisitDays['> 60%'] += x['visit_days']
          } else if (x['housing_cost_burden'] > 40) {
            housingCostBurdenVisitDays['> 40%'] += x['visit_days']
          } else if (x['housing_cost_burden'] > 20) {
            housingCostBurdenVisitDays['> 20%'] += x['visit_days']
          } else {
            housingCostBurdenVisitDays['> 0%'] += x['visit_days']
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

        this._makeBarChart(housingCostBurdenVisitDays, '#housing-cost-burden-chart', 'Housing Cost Burden');
        this._makeBarChart(sviVisitDays, '#svi-chart', 'Social Vulnerability Index');

      },
      _calculateValues: function () {
        let self = this;
        let population = 0, housingCostBurdenPercentage = 0, minorityPercentage = 0, svi = 0, totalVisitDays = 0;
        for (const t of self.demographicData) {
          const visitDays = self._nanToZero(t['visit_days']);
          population += self._nanToZero(t['population']);
          housingCostBurdenPercentage += self._nanToZero(t['housing_cost_burden']) * visitDays;
          minorityPercentage += self._nanToZero(t['minority_percentage']) * visitDays;
          svi += self._nanToZero(t['svi']) * visitDays;
          totalVisitDays += visitDays;
        }

        if (totalVisitDays === 0) {
          totalVisitDays = 1
        }
        self.totalPopulation = population;
        self.totalVisitDays = totalVisitDays;
        self.weightedHousingCostBurdenPercentage = self._nDecimalPlaces(housingCostBurdenPercentage / totalVisitDays, 2);
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
@import "../assets/styles/info-icon.css";
  .demographics-container {
    position: relative; /* so the overlay can be absolutely positioned */
    min-height: 72vh;   /* or whatever is needed for your layout */
  }
  .list-group-item {
    padding: 5px 10px 5px 10px;
  }
  .list-group-item .value {
    float: right;
    padding-right: 15px;
    font-weight: bold;
    opacity: 0.7;
  }
</style>
