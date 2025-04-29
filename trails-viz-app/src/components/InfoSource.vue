<template>
  <div class="info-source-container">
    <div class="controls-container">
      <span class="controls-label mr-2">Display Mode:</span>
      <b-form-radio-group v-model="displayMode" @change="renderInfoSource">
        <b-form-radio value="count">Count</b-form-radio>
        <b-form-radio value="percentage">%</b-form-radio>
      </b-form-radio-group>
    </div>
    <div id="info-source-chart"></div>
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading data...</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import c3 from 'c3';
import { VIZ_MODES, BRAND_COLORS } from '../store/constants';

export default {
  name: "InfoSource",
  data() {
    return {
      loading: false,
      infoSourceData: null,
      displayMode: 'count'  // 'count' or 'percentage'
    }
  },
  computed: {
    yearRange() {
      return this.$store.getters.getYearRange;
    }
  },
  watch: {
    yearRange() {
      this.renderInfoSource();
    }
  },
  methods: {
    renderInfoSource() {
      this.loading = true;
      const vizMode = this.$store.getters.getVizMode;

      this.projectCode = this.$store.getters.getSelectedProjectCode;
      this.siteid = this.$store.getters.getSelectedSite['siteid'];

      let url;
      if (vizMode === VIZ_MODES.PROJECT) {
        url = `${this.$apiEndpoint}/projects/${this.projectCode}/categoricalChatbotData/InfoSource`;
      } else if (vizMode === VIZ_MODES.SITE) {
        url = `${this.$apiEndpoint}/sites/${this.siteid}/categoricalChatbotData/InfoSource`;
      }

      const yrRange = this.yearRange;
      if (yrRange && yrRange.length === 2) {
        url += `?year_start=${yrRange[0]}&year_end=${yrRange[1]}`;
      }

      axios.get(url)
        .then(response => {
          this.infoSourceData = response.data.InfoSource;

          const sortedPairs = Object.entries(this.infoSourceData).sort((a, b) => b[1] - a[1]);
          const categories = sortedPairs.map(pair => pair[0]);
          const counts = sortedPairs.map(pair => pair[1]);

          let values = [...counts];
          let yLabel = 'Count';

          if (this.displayMode === 'percentage') {
            const total = counts.reduce((acc, val) => acc + val, 0);
            values = counts.map(count => ((count / total) * 100).toFixed(2));
            yLabel = '%';
          }

          c3.generate({
            bindto: '#info-source-chart',
            size: { height: 500 },
            bar: { ratio: 0.9 },
            padding: { top: 20 },
            data: {
              columns: [[yLabel, ...values]],
              type: 'bar',
              [ yLabel ]: BRAND_COLORS.primary
            },
            legend: { show: false },
            axis: {
              rotated: true,
              x: {
                type: 'category',
                categories: categories,
                label: { text: 'Information Source', position: 'outer-middle' },
                tick: { rotate: 45, multiline: false }
              },
              y: {
                label: { text: yLabel, position: 'outer-center' }
              }
            },
            tooltip: {
              format: {
                value: value => this.displayMode === 'percentage' ? `${value}%` : value
              }
            }
          });
        })
        .finally(() => {
          this.loading = false;
        });
    }
  }
};
</script>

<style scoped>
.info-source-container {
  position: relative;
  min-height: 72vh;
  font-family: 'Roboto Condensed', sans-serif;
}
.controls-container {
  display: flex;
  align-items: center;
}
.controls-label {
  font-weight: 500;
  margin-right: 1rem;
}
::v-deep #info-source-chart .c3-axis-x .tick line {
  display: none;
}
</style>
