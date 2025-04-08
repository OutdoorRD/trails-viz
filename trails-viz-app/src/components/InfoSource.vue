<template>
    <div class="info-source-container">
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
  import { VIZ_MODES } from '../store/constants';

  export default {
    name: "InfoSource",
    data() {
      return {
        loading: false,
        infoSourceData: null
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
        let vizMode = this.$store.getters.getVizMode;

        this.projectName = this.$store.getters.getSelectedProjectName;
        this.projectCode = this.$store.getters.getSelectedProjectCode;
        this.siteid = this.$store.getters.getSelectedSite['siteid'];

        let url;
        if (vizMode === VIZ_MODES.PROJECT) {
          url = this.$apiEndpoint + '/projects/' + this.projectCode + '/categoricalChatbotData/InfoSource';
        } else if (vizMode === VIZ_MODES.SITE) {
          url = this.$apiEndpoint + '/sites/' + this.siteid + '/categoricalChatbotData/InfoSource';
        }

        const yrRange = this.$store.getters.getYearRange;
        if (yrRange && yrRange.length === 2) {
          const yearStart = yrRange[0];
          const yearEnd = yrRange[1];
          url += `?year_start=${yearStart}&year_end=${yearEnd}`;
        }
        // Fetch data without any auth header.
        axios.get(url)
          .then(response => {
            this.infoSourceData = response.data.InfoSource;
            // Convert the response object into an array of [key, value] pairs then sort descending by value.
            const sortedPairs = Object.entries(this.infoSourceData).sort((a, b) => b[1] - a[1]);
            const categories = sortedPairs.map(pair => pair[0]);
            const counts = sortedPairs.map(pair => pair[1]);
            
            // Render a simple bar chart with c3.
            c3.generate({
              bindto: '#info-source-chart',
              data: {
                columns: [
                  ['Count', ...counts]
                ],
                type: 'bar'
              },
              legend: {
                show: false
              },
              axis: {
                x: {
                  type: 'category',
                  categories: categories,
                  label: {
                    text: 'Information Source',
                    position: 'outer-center'
                  },
                  tick: {
                    rotate: 45,
                    multiline: false
                  }
                },
                y: {
                  label: {
                    text: 'Count',
                    position: 'outer-middle'
                  }
                }
              }
            });
          })
          .finally(() => {
            this.loading = false;
          });
      }
    },
    mounted() {
      this.renderInfoSource();
    }
  };
  </script>

  <style scoped>
  @import "../assets/styles/loading-spinner.css";
  @import "../assets/styles/info-icon.css";
    .info-source-container {
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
  
  <!-- <style scoped>
  .chart-container {
    position: relative;
    height: 72vh;
    max-width: 600px;
    margin: 20px auto;
  }
  
  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.7);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  
  .loading-spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-left-color: #777;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
  }
  
  .loading-text {
    margin-top: 10px;
    font-size: 14px;
    color: #333;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  </style>
   -->