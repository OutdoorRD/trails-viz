<template>
  <div class="party-characteristics-container">
  <!-- 1) Loading overlay -->
  <div v-if="loading" class="loading-overlay">
    <div class="loading-spinner"></div>
    <p class="loading-text">Loading data...</p>
  </div>
  <div>
    <!-- Number of Responses -->
    <div>
      <b-row class="mt-4">
        <b-col sm="12">
          <h4 class="section-title">Number of Responses</h4>
          <div class="table-container">
            <b-table
              :items="tableData"
              :fields="tableFields"
              responsive="sm"
              bordered
              hover
              head-variant="light"
            >
            </b-table>
          </div>
        </b-col>
      </b-row>
      <hr class="section-separator" />
    </div>

    <!-- Yearly Average Response -->
    <div>
      <b-row class="mt-4">
        <b-col sm="12">
          <h4 class="section-title">Yearly Average Response</h4>
        </b-col>

        <!-- Party People TimeSeries -->
        <b-col sm="12" v-if="timeSeriesFetchStatus.PartyPeople === 200">
          <div id="party-people-timeseries" class="chart-container"></div>
        </b-col>

        <!-- Party Vehicles TimeSeries -->
        <b-col sm="12" v-if="timeSeriesFetchStatus.PartyVehics === 200">
          <div id="party-vehicles-timeseries" class="chart-container"></div>
        </b-col>

        <!-- Trail Visits TimeSeries -->
        <b-col sm="12" v-if="timeSeriesFetchStatus.TrailVisits === 200">
          <div id="trail-visits-timeseries" class="chart-container"></div>
        </b-col>

        <!-- People Per Vehicle TimeSeries -->
        <b-col sm="12" v-if="timeSeriesFetchStatus.PeoplePerVehics === 200">
          <div id="people-per-vehicle-timeseries" class="chart-container"></div>
        </b-col>
      </b-row>
      <hr class="section-separator" />
    </div>

    <!-- Distribution of Responses -->
    <div>
      <b-row class="mt-4">
        <b-col sm="12">
          <h4 class="section-title">Distribution of Responses</h4>
          <div class="controls-container d-flex flex-column">
            <div class="d-flex align-items-center mb-2">
              <span class="controls-label mr-2">Select Year(s):</span>
              <div class="d-flex flex-wrap">
                <!-- Exclude the Total column from these checkboxes -->
                <b-form-checkbox
                  v-for="field in tableFields.slice(1).filter(field => field.key !== 'Total')"
                  :key="field.key"
                  :value="field.key"
                  v-model="selectedYears"
                  class="mr-3"
                >
                  {{ field.label }}
                </b-form-checkbox>
              </div>
            </div>
            <!-- Show Total toggle -->
            <div class="d-flex align-items-center mb-2">
              <span class="controls-label mr-2">Show Total:</span>
              <b-form-checkbox v-model="showTotal" class="mr-3">
                Across Years
              </b-form-checkbox>
            </div>
            <!-- Display Mode -->
            <div class="d-flex align-items-center">
              <span class="controls-label mr-2">Display Mode:</span>
              <b-form-radio-group v-model="displayMode" @change="updateCharts" class="radio-group">
                <b-form-radio value="count">Count</b-form-radio>
                <b-form-radio value="%">%</b-form-radio>
              </b-form-radio-group>
            </div>
          </div>
        </b-col>
        <!-- Party People Chart -->
        <b-col sm="12" v-if="barDataFetchStatus.PartyPeople === 200">
          <div id="party-people-chart" class="chart-container"></div>
        </b-col>

        <!-- Party Vehicles Chart -->
        <b-col sm="12" class="mt-3" v-if="barDataFetchStatus.PartyVehics === 200">
          <div id="party-vehicles-chart" class="chart-container"></div>
        </b-col>

        <!-- Trail Visits Chart -->
        <b-col sm="12" v-if="barDataFetchStatus.TrailVisits === 200">
          <div id="trail-visits-chart" class="chart-container"></div>
        </b-col>
      </b-row>
    </div>
  </div>
  </div>
</template>

<script>
import c3 from 'c3';
import axios from 'axios';
import { VIZ_MODES } from "../store/constants";

const CHARACTERISTIC_DISPLAY_NAMES = {
  PartyVehics: "Number of Vehicles Per Party",
  PartyPeople: "Number of People Per Party",
  TrailVisits: "Number of Trail Visits In Past 12 Months",
  PeoplePerVehics: "Number of People Per Vehicle (Calculated)"
};

export default {
  name: "PartyCharacteristics",
  data() {
    return {
      // Basic State
      loading: false,
      projectName: null,
      projectCode: null,
      siteid: null,
      showTotal: false,

      characteristics: ['TrailVisits', 'PartyPeople', 'PartyVehics', 'PeoplePerVehics'],

      // Storage for bar data (raw responses) by characteristic
      rawData: {
        TrailVisits: [],
        PartyPeople: [],
        PartyVehics: [],
        PeoplePerVehics: [],
      },

      // Storage for time-series data by characteristic
      timeSeriesData: {
        TrailVisits: null,
        PartyPeople: null,
        PartyVehics: null,
        PeoplePerVehics: null,
      },

      // Track fetch statuses for conditional rendering of charts
      barDataFetchStatus: {
        TrailVisits: null,
        PartyPeople: null,
        PartyVehics: null,
        PeoplePerVehics: null,
      },
      timeSeriesFetchStatus: {
        TrailVisits: null,
        PartyPeople: null,
        PartyVehics: null,
        PeoplePerVehics: null,
      },

      // Display mode states
      displayMode: 'count', // 'count' or '%'
      selectedYears: [],

      // Table
      tableFields: [],
      tableData: [],

      // Combined raw data from all characteristics, only used for table and distribution charts
      combinedRawData: [],
    };
  },
  computed: {
    vizMode() {
      return this.$store.getters.getVizMode;
    },
    yearRange() {
      return this.$store.getters.getYearRange;
    }
  },
  watch: {
    yearRange() {
      this.renderPartyCharacteristics();
    }
  },
  methods: {
    renderPartyCharacteristics() {
      this.loading = true;
      this.projectName = this.$store.getters.getSelectedProjectName;
      this.projectCode = this.$store.getters.getSelectedProjectCode;
      this.siteid = this.$store.getters.getSelectedSite['siteid'];

      // If projectCode or siteid not ready, skip
      if (!this.projectCode && this.vizMode === VIZ_MODES.PROJECT) return;
      if (!this.siteid && this.vizMode !== VIZ_MODES.PROJECT) return;

      Promise.all([
        this.fetchAllBarData(),
        this.fetchAllTimeSeriesData()
      ]).then(() => {
        this.generateTableData(this.combinedRawData);
        this.updateCharts();
        this.renderTimeSeriesCharts();
      })
      .finally(() => {
        this.loading = false;
      });
    },

    // ------------------------------------------
    // FETCH BAR DATA FOR ALL CHARACTERISTICS
    // ------------------------------------------
    fetchAllBarData: function() {
      const requests = this.characteristics.map((char) =>
        this.fetchBarDataByCharacteristic(char)
      );
      return Promise.all(requests).then(() => {
        // Build "combinedRawData" from each characteristic's array
        this.combinedRawData = [
          ...this.rawData.PartyPeople,
          ...this.rawData.PartyVehics,
          ...this.rawData.TrailVisits,
          ...this.rawData.PeoplePerVehics,
        ];
      });
    },


    fetchBarDataByCharacteristic: function(char) {
      const endpoint =
        this.vizMode === VIZ_MODES.PROJECT
          ? `${this.$apiEndpoint}/projects/${this.projectCode}/chatbotData/${char}`
          : `${this.$apiEndpoint}/sites/${this.siteid}/chatbotData/${char}`;
      
      const yearRange = this.yearRange;
      if (yearRange && yearRange.length === 2) {
        const [yearStart, yearEnd] = yearRange;
        endpoint += `?year_start=${yearStart}&year_end=${yearEnd}`;
      }

      return axios
        .get(endpoint)
        .then((response) => {
          this.barDataFetchStatus[char] = response.status;
          if (response.status === 200) {
            const aggregatedData = response.data[char];
            const transformedData = [];
            Object.keys(aggregatedData).forEach((year) => {
              const counts = aggregatedData[year];
              // Compute the total count for the year
              const total = Object.values(counts).reduce((acc, count) => acc + count, 0);
              transformedData.push({
                characteristic: char,
                year: year,
                value: total,
                counts: counts,
              });
            });
            this.rawData[char] = transformedData;
          } else {
            this.rawData[char] = [];
          }
        })
        .catch((err) => {
          this.barDataFetchStatus[char] = err.response ? err.response.status : 500;
          this.rawData[char] = [];
        });
    },

    // ------------------------------------------
    // FETCH TIME-SERIES DATA FOR ALL CHARACTERISTICS
    // ------------------------------------------
    fetchAllTimeSeriesData: function() {
      const requests = this.characteristics.map((char) =>
        this.fetchTimeSeriesDataByCharacteristic(char)
      );
      return Promise.all(requests);
    },

    fetchTimeSeriesDataByCharacteristic: function(char) {
      const endpoint =
        this.vizMode === VIZ_MODES.PROJECT
          ? `${this.$apiEndpoint}/projects/${this.projectCode}/chatbotDataYearlyStatistics/${char}`
          : `${this.$apiEndpoint}/sites/${this.siteid}/chatbotDataYearlyStatistics/${char}`;
      const yearRange = this.yearRange;
      if (yearRange && yearRange.length === 2) {
        const [yearStart, yearEnd] = yearRange;
        endpoint += `?year_start=${yearStart}&year_end=${yearEnd}`;
      }
      return axios
        .get(endpoint)
        .then((response) => {
          this.timeSeriesFetchStatus[char] = response.status;
          if (response.status === 200) {
            this.timeSeriesData[char] = response.data;
          } else {
            this.timeSeriesData[char] = null;
          }
        })
        .catch((err) => {
          this.timeSeriesFetchStatus[char] = err.response ? err.response.status : 500;
          this.timeSeriesData[char] = null;
        });
    },

    // ------------------------------------------
    // TABLE & DISTRIBUTION CHARTS
    // ------------------------------------------
    generateTableData(data) {
      const yearSet = new Set(data.map((item) => item.year));
      const characteristics = [...new Set(data.map((item) => item.characteristic))];

      // Create dynamic table fields (years as columns) + "Total"
      this.tableFields = [
        { key: "characteristic", label: "Characteristic" },
        ...[...yearSet].sort().map((year) => ({
          key: year.toString(),
          label: year.toString(),
          isYear: true,
        })),
      ];

      // Initialize selectedYears with all years
      this.selectedYears = [...yearSet].map((y) => y.toString());

      // Create table data rows
      const tableRows = characteristics.map((char) => {
        const row = {
          characteristic: CHARACTERISTIC_DISPLAY_NAMES[char] || char,
        };

        [...yearSet].forEach((year) => {
          const countForYear = data
            .filter(
              (item) =>
                item.characteristic === char &&
                item.year.toString() === year.toString()
            )
            .reduce((acc, item) => acc + item.value, 0);
          row[year] = countForYear;
        });
        return row;
      });

      this.tableData = tableRows;
    },


    updateCharts() {

      const yearlyData = this.yearlyCounts(this.combinedRawData);
      this.chartData = yearlyData;

      // Render the bar charts if their fetch status == 200
      if (this.barDataFetchStatus['PartyVehics'] === 200) {
        this._makePartyVehiclesChart(this.chartData);
      }
      if (this.barDataFetchStatus['PartyPeople'] === 200) {
        this._makePartyPeopleChart(this.chartData);
      }
      if (this.barDataFetchStatus['TrailVisits'] === 200) {
        this._makeTrailVisitsChart(this.chartData);
      }
    },
  
    yearlyCounts(data) {
      const result = {
        PartyVehics: {},
        PartyPeople: {},
        TrailVisits: {},
        PeoplePerVehics: {},
      };

      data.forEach((item) => {
        const { characteristic, year, counts } = item;
        if (year === "Total") {
          if (!this.showTotal) return;
        } else {
          if (!this.selectedYears.includes(year.toString())) return;
        }
        if (!result[characteristic][year]) {
          result[characteristic][year] = {};
        }
        Object.keys(counts).forEach((cat) => {
          result[characteristic][year][cat] =
            (result[characteristic][year][cat] || 0) + counts[cat];
        });
      });

      return result;
    },

    _makePartyVehiclesChart(data) {
      this._makeBarChart(data.PartyVehics, '#party-vehicles-chart', CHARACTERISTIC_DISPLAY_NAMES.PartyVehics);
    },
    _makePartyPeopleChart(data) {
      this._makeBarChart(data.PartyPeople, '#party-people-chart', CHARACTERISTIC_DISPLAY_NAMES.PartyPeople);
    },
    _makeTrailVisitsChart(data) {
      this._makeBarChart(data.TrailVisits, '#trail-visits-chart', CHARACTERISTIC_DISPLAY_NAMES.TrailVisits);
    },

    _makeBarChart(data, htmlElemId, title) {
      const displayMode = this.displayMode;
      const categoriesSet = new Set();

      // 1) Gather categories
      Object.keys(data).forEach((yearOrAll) => {
        const counts = data[yearOrAll] || {};
        Object.keys(counts).forEach((cat) => {
          if (counts[cat] > 0) categoriesSet.add(cat);
        });
      });

      // 2) Sort categories
      const categories = [...categoriesSet].sort((a, b) =>
        a === '3+' ? 1 : parseInt(a, 10) - parseInt(b, 10)
      );

      // 3) Build columns for c3
      const columns = [];
      const sortedKeys = Object.keys(data).sort((a, b) => {
        if (a === 'Total') return -1;
        if (b === 'Total') return 1;
        return parseInt(a) - parseInt(b);
      });

      sortedKeys.forEach((yearOrAll) => {
        let values = categories.map((cat) => data[yearOrAll][cat] || 0);
        if (displayMode === '%') {
          const total = values.reduce((acc, val) => acc + val, 0);
          values = total > 0 ? values.map(v => ((v / total) * 100).toFixed(2)) : values.map(() => 0);
        }
        // Insert label as first item
        values.unshift(yearOrAll.toString());
        columns.push(values);
      });

      c3.generate({
        bindto: htmlElemId,
        size: { height: 200 },
        axis: {
          x: {
            type: 'category',
            categories: categories,
            label: {
              text: title,
              position: 'outer-center'
            },
            tick: { multiline: false },
            height: 40
          },
          y: {
            label: {
              text: displayMode === '%' ? '%' : 'Count',
              position: 'outer-middle'
            }
          }
        },
        data: {
          columns: columns,
          type: 'bar',
          colors: {
            'Total': '#FF5733'
          }
        },
        tooltip: {
          order: null,
          format: {
            value(value) {
              return displayMode === '%' ? `${value}%` : value;
            }
          }
        }
      });
    },

    // ------------------------------------------
    // TIME-SERIES CHARTS
    // ------------------------------------------
    renderTimeSeriesCharts() {
      // For each characteristic, if we have a 200 fetch, and the data is not null, render
      if (this.timeSeriesFetchStatus.PartyVehics === 200 && this.timeSeriesData.PartyVehics) {
        this._makePartyVehiclesTimeSeriesChart(this.timeSeriesData.PartyVehics);
      }
      if (this.timeSeriesFetchStatus.PartyPeople === 200 && this.timeSeriesData.PartyPeople) {
        this._makePartyPeopleTimeSeriesChart(this.timeSeriesData.PartyPeople);
      }
      if (this.timeSeriesFetchStatus.TrailVisits === 200 && this.timeSeriesData.TrailVisits) {
        this._makeTrailVisitsTimeSeriesChart(this.timeSeriesData.TrailVisits);
      }
      if (this.timeSeriesFetchStatus.PeoplePerVehics === 200 && this.timeSeriesData.PeoplePerVehics) {
        this._makePeoplePerVehicleTimeSeriesChart(this.timeSeriesData.PeoplePerVehics);
      }
    },

    _makePartyVehiclesTimeSeriesChart(data) {
      this._makeTimeSeriesChart(data.years, data.PartyVehics, '#party-vehicles-timeseries', CHARACTERISTIC_DISPLAY_NAMES.PartyVehics);
    },
    _makePartyPeopleTimeSeriesChart(data) {
      this._makeTimeSeriesChart(data.years, data.PartyPeople, '#party-people-timeseries', CHARACTERISTIC_DISPLAY_NAMES.PartyPeople);
    },
    _makeTrailVisitsTimeSeriesChart(data) {
      this._makeTimeSeriesChart(data.years, data.TrailVisits, '#trail-visits-timeseries', CHARACTERISTIC_DISPLAY_NAMES.TrailVisits);
    },
    _makePeoplePerVehicleTimeSeriesChart(data) {
      this._makeTimeSeriesChart(data.years, data.PeoplePerVehics, '#people-per-vehicle-timeseries', CHARACTERISTIC_DISPLAY_NAMES.PeoplePerVehics);
    },

    /**
     * @param {array} labels array of years
     * @param {object} featureData  {lower_bound:[], mean:[], upper_bound:[]}
     * @param {string} htmlElemId chart container
     * @param {string} title
     */
    _makeTimeSeriesChart(labels, featureData, htmlElemId, title) {
      if (!featureData) return;

      c3.generate({
        bindto: htmlElemId,
        data: {
          x: 'x',
          columns: [
            ['x', ...labels],
            ['Lower Bound (95%)', ...(featureData.lower_bound || [])],
            ['Upper Bound (95%)', ...(featureData.upper_bound || [])],
            ['Mean', ...(featureData.mean || [])]
          ],
          types: {
            Mean: 'line',
            'Upper Bound (95%)': 'line',
            'Lower Bound (95%)': 'line'
          },
          colors: {
            Mean: 'blue',
            'Upper Bound (95%)': 'lightblue',
            'Lower Bound (95%)': 'lightblue'
          }
        },
        axis: {
          x: {
            type: 'category',
            label: {
              text: 'Year',
              position: 'outer-center'
            },
            tick: { multiline: false },
            height: 40
          },
          y: {
            label: {
              text: title,
              position: 'outer-middle'
            }
          }
        },
        tooltip: {
          grouped: false
        }
      });
    },
  },

  watch: {
    selectedYears() {
      this.updateCharts();
    },
    displayMode() {
      this.updateCharts();
    },
    showTotal() {
      this.updateCharts();
    }
  },

  mounted() {
    this.renderPartyCharacteristics();
  },
};
</script>

<style scoped>
  .party-characteristics-container {
    position: relative;
    min-height: 75vh; /* Enough height so overlay covers the entire area */
  }
 
</style>
