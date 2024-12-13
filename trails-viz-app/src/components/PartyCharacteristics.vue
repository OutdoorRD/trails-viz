<template>
  <div>
    <!-- Number of Responses -->
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

    <!-- Yearly Average Response -->
    <b-row class="mt-4">
      <b-col sm="12">
        <h4 class="section-title">Yearly Average Response</h4>
      </b-col>

      <b-col sm="12">
        <div id="party-vehicles-timeseries" class="chart-container"></div>
      </b-col>
      <b-col sm="12">
        <div id="party-people-timeseries" class="chart-container"></div>
      </b-col>
      <b-col sm="12">
        <div id="trail-visits-timeseries" class="chart-container"></div>
      </b-col>
      <b-col sm="12">
        <div id="people-per-vehicle-timeseries" class="chart-container"></div>
      </b-col>
    </b-row>

    <hr class="section-separator" />

  <!-- Distribution of Responses -->
  <b-row class="mt-4">
    <b-col sm="12">
      <h4 class="section-title">Distribution of Responses</h4>
      <div class="controls-container d-flex align-items-center">
        <span class="controls-label mr-2">Select Year(s):</span>
        <div class="d-flex flex-wrap">
          <b-form-checkbox
            v-model="allYearsSelected"
            class="mr-3"
          >
            All Years
          </b-form-checkbox>
          <b-form-checkbox
            v-for="field in tableFields.slice(1).filter(field => field.key !== 'total')"
            :key="field.key"
            :value="field.key"
            v-model="selectedYears"
            class="mr-3"
          >
            {{ field.label }}
          </b-form-checkbox>
        </div>
      </div>
    </b-col>

    <b-col sm="12" class="mt-3">
      <div class="controls-container d-flex align-items-center">
        <span class="controls-label mr-2">Display Mode:</span>
        <b-form-radio-group v-model="displayMode" @change="updateCharts" class="radio-group">
        <b-form-radio value="count">Count</b-form-radio>
        <b-form-radio value="%">%</b-form-radio>
      </b-form-radio-group>

      </div>
    </b-col>

    <b-col sm="12" class="mt-3">
      <div id="party-vehicles-chart" class="chart-container"></div>
    </b-col>
    <b-col sm="12">
      <div id="party-people-chart" class="chart-container"></div>
    </b-col>
    <b-col sm="12">
      <div id="trail-visits-chart" class="chart-container"></div>
    </b-col>
  </b-row>
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
      projectName: null,
      projectCode: null,
      siteid: null,
      chartData: null,
      timeSeriesData: null,
      displayMode: 'count', // 'count' or '%'
      tableFields: [],
      tableData: [],
      selectedYears: [],
      allYears: [],
      allYearsString: [],
      allSelected: false,
      rawData: [],
      allYearsSelected: false
    };
  },
  methods: {
    renderPartyCharacteristics() {
      const vizMode = this.$store.getters.getVizMode;
      this.projectName = this.$store.getters.getSelectedProjectName;
      this.projectCode = this.$store.getters.getSelectedProjectCode;
      this.siteid = this.$store.getters.getSelectedSite['siteid'];

      // If projectCode or siteid is not available yet, skip fetching
      if (!this.projectCode && vizMode === VIZ_MODES.PROJECT) return;
      if (!this.siteid && vizMode !== VIZ_MODES.PROJECT) return;


      const barChartEndpoint = vizMode === VIZ_MODES.PROJECT
        ? `${this.$apiEndpoint}/projects/${this.projectCode}/partyCharacteristics`
        : `${this.$apiEndpoint}/sites/${this.siteid}/partyCharacteristics`;

      const timeSeriesEndpoint = vizMode === VIZ_MODES.PROJECT
        ? `${this.$apiEndpoint}/projects/${this.projectCode}/partyCharacteristicsYearlyStatistics`
        : `${this.$apiEndpoint}/sites/${this.siteid}/partyCharacteristicsYearlyStatistics`;

      axios.get(barChartEndpoint)
        .then(response => {
          this.rawData = response.data;
          this.generateTableData(this.rawData);
          this.chartData = this.yearlyCounts(this.rawData);
          this.updateCharts();
        });

      axios.get(timeSeriesEndpoint)
        .then(response => {
          this.timeSeriesData = response.data;
          this._makePartyPeopleTimeSeriesChart(this.timeSeriesData);
          this._makePartyVehiclesTimeSeriesChart(this.timeSeriesData);
          this._makeTrailVisitsTimeSeriesChart(this.timeSeriesData);
          this._makePeoplePerVehicleTimeSeriesChart(this.timeSeriesData);
        });
    },
    generateTableData(data) {
      const yearSet = new Set(data.map((item) => item.year));
      const characteristics = [...new Set(data.map((item) => item.characteristic))];

      // Create dynamic table fields (years as columns) and add the "Total" column
      this.tableFields = [
        { key: "characteristic", label: "Characteristic" },
        ...[...yearSet].sort().map((year) => ({
          key: year.toString(),
          label: year.toString(),
          isYear: true,
        })),
        { key: "total", label: "Total" }, // Add the "Total" column
      ];

      // Initialize selectedYears with all years
      this.selectedYears = [...yearSet].map((year) => year.toString());

      // Create table data rows
      const tableRows = characteristics.map((characteristic) => {
        const row = { 
          characteristic: CHARACTERISTIC_DISPLAY_NAMES[characteristic] || characteristic 
        };

        // Populate counts for each year
        [...yearSet].forEach((year) => {
          const count = data.filter(
            (item) =>
              item.characteristic === characteristic && item.year === year
          ).length;
          row[year] = count;
        });

        // Compute the total for each row
        row.total = [...yearSet].reduce((sum, year) => sum + (row[year] || 0), 0);

        return row;
      });

      this.tableData = tableRows;
    },
    allYearsCounts(data) {
      const result = {
        PartyVehics: {},
        PartyPeople: {},
        TrailVisits: {}
      };

      // Process the data
      data.forEach(item => {
        const { characteristic, value} = item;

        // Skip PeoplePerVehics for bar chart aggregation
        if (characteristic === 'PeoplePerVehics') {
          return;
        }

        if (!result[characteristic]['all_years']) {
          result[characteristic]['all_years'] = [];
        }
        result[characteristic]['all_years'].push(value);

      });

      // Group and count values for each characteristic and year
      const aggregatedResult = {};
      Object.keys(result).forEach(characteristic => {
        aggregatedResult[characteristic] = this.groupAndCount(result[characteristic]['all_years']);
      });

      return aggregatedResult;
    }
    ,
    yearlyCounts(data) {
      const result = {
        PartyVehics: {},
        PartyPeople: {},
        TrailVisits: {}
      };

      // Process the data and filter by selected years
      data.forEach(item => {
        const { characteristic, value, year } = item;

        // Skip PeoplePerVehics for bar chart aggregation
        if (characteristic === 'PeoplePerVehics') {
          return;
        }

        // Only include data for the selected years
        if (this.selectedYears.includes(year.toString())) {
          if (!result[characteristic][year]) {
            result[characteristic][year] = [];
          }
          result[characteristic][year].push(value);
        }
      });

      // Group and count values for each characteristic and year
      const aggregatedResult = {};
      Object.keys(result).forEach(characteristic => {
        aggregatedResult[characteristic] = {};
        Object.keys(result[characteristic]).forEach(year => {
          aggregatedResult[characteristic][year] = this.groupAndCount(result[characteristic][year]);
        });
      });

      return aggregatedResult;
    }
    ,
    groupAndCount(data) {
      const counts = { '0': 0, '1': 0, '2': 0, '3+': 0 };

      if (!Array.isArray(data)) {
        return counts
      }

      data.forEach(value => {
        if (value === 0) counts['0']++;
        else if (value === 1) counts['1']++;
        else if (value === 2) counts['2']++;
        else counts['3+']++;
      });
      return counts;
    },
    mergeYearlyAndAllYearsCounts(yearlyData, allYearsData){
      // Create a deep clone of the yearly data to avoid modifying the original
      const mergedData = JSON.parse(JSON.stringify(yearlyData));

      // Iterate over each characteristic
      Object.keys(allYearsData).forEach(characteristic => {
        if (!mergedData[characteristic]) {
          mergedData[characteristic] = {};
        }
        // Add the "All Years" key with its corresponding values
        mergedData[characteristic]["All Years"] = allYearsData[characteristic];
      });

      return mergedData;
    },
    updateCharts() {
      const yearlyData = this.yearlyCounts(this.rawData);
      if (this.allYearsSelected) {
        const allYearsData = this.allYearsCounts(this.rawData);
        this.chartData = this.mergeYearlyAndAllYearsCounts(yearlyData, allYearsData)
      } else {
        this.chartData = yearlyData;
      }
      this._makePartyVehiclesChart(this.chartData);
      this._makeTrailVisitsChart(this.chartData);
      this._makePartyPeopleChart(this.chartData);
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

      // Collect all categories from years and "All"
      Object.keys(data).forEach(yearOrAll => {
        const counts = data[yearOrAll] || {};
        Object.keys(counts).forEach(cat => {
          if (counts[cat] > 0) {
            categoriesSet.add(cat);
          }
        });
      });

      // Convert categoriesSet to a sorted array
      const categories = [...categoriesSet].sort((a, b) => (a === '3+' ? 1 : parseInt(a, 10) - parseInt(b, 10)));

      const columns = [];

        // Sort keys so "All" comes first
      const sortedKeys = Object.keys(data).sort((a, b) => (a === 'All' ? -1 : b === 'All' ? 1 : a - b));

      sortedKeys.forEach(yearOrAll => {
        const counts = data[yearOrAll] || {};
        let values = categories.map(cat => counts[cat] || 0);

        if (displayMode === '%') {
          const total = values.reduce((sum, val) => sum + val, 0);
          values = total > 0 ? values.map(val => ((val / total) * 100).toFixed(2)) : values.map(() => 0);
        }
        values.unshift(yearOrAll.toString()); // Add year or "All" label as the first value
        columns.push(values);
      });

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
              text: displayMode === '%' ? '%' : 'Count',
              position: 'outer-middle'
            }
          }
        },
        data: {
          columns: columns,
          type: 'bar'
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
    }
    ,
    _makePartyPeopleTimeSeriesChart: function (data) {
      this._makeTimeSeriesChart(data.labels, data.PartyPeople, '#party-people-timeseries', CHARACTERISTIC_DISPLAY_NAMES.PartyPeople);
    },

    _makePartyVehiclesTimeSeriesChart: function (data) {
      this._makeTimeSeriesChart(data.labels, data.PartyVehics, '#party-vehicles-timeseries', CHARACTERISTIC_DISPLAY_NAMES.PartyVehics);
    },

    _makeTrailVisitsTimeSeriesChart: function (data) {
      this._makeTimeSeriesChart(data.labels, data.TrailVisits, '#trail-visits-timeseries', CHARACTERISTIC_DISPLAY_NAMES.TrailVisits);
    },
    
    _makePeoplePerVehicleTimeSeriesChart: function(data) {
      this._makeTimeSeriesChart(data.labels, data.PeoplePerVehics, '#people-per-vehicle-timeseries', CHARACTERISTIC_DISPLAY_NAMES.PeoplePerVehics)
    },
    _makeTimeSeriesChart: function (labels, featureData, htmlElemId, title) {
      c3.generate({
        bindto: htmlElemId,
        data: {
          x: 'x',
          columns: [
            ['x', ...labels],
            ['Lower Bound (95%)', ...featureData.lower_bound],
            ['Upper Bound (95%)', ...featureData.upper_bound],
            ['Mean', ...featureData.mean]
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
            tick: {
              multiline: false
            },
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
    }

  },
  watch: {
    selectedYears() {
      this.updateCharts();
    },
    allYearsSelected() {
      this.updateCharts();
    },
    displayMode() {
      this.updateCharts();
    }
  },
  mounted() {
    this.renderPartyCharacteristics();
  }
};
</script>
