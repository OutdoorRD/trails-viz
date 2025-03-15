<template>
  <div class="time-series-container">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading data...</p>
    </div>
    <b-row no-gutters class="align-items-top justify-content-end mt-2">
      <b-col cols="auto">
        <b-radio-group v-model="dataRange" :options="dateRangeOptions" v-on:input="switchDateRange"></b-radio-group>
      </b-col>
      <b-col cols="auto">
      <b-button
        variant="outline-primary"
        size="sm"
        @click="downloadData"
        :disabled="isDownloading"
      >
        <i class="fas fa-download mr-1"></i> Download Data
      </b-button>
    </b-col>
    </b-row>
    <div id="time-series"></div>
    <div class="text-center disclaimer">
      <p>
        <strong>"Modeled"</strong> values here are in draft form and will change, sometimes dramatically, as our methods and data improve.
        <br>
        <strong>"On-site"</strong> values are estimates from infrared counters and parking lot counts, where available.
      </p>
    </div>
  </div>
</template>

<script>
  import {COLORS, VIZ_MODES} from '../store/constants'
  import axios from 'axios'
  import c3 from 'c3'
  import JSZip from "jszip";
  import FileSaver from "file-saver";

  Number.prototype.pad = function (size) {
    let s = String(this);
    while (s.length < (size || 2)) {s = "0" + s;}
    return s;
  };

  export default {
    name: "TimeSeries",
    data: function() {
      return {
        loading: false,
        isDownloading: false,
        projectName: null,
        projectCode: null,
        siteid: null,
        trailName: null,
        selectedSite: null,
        monthlyVisitation: null,
        weeklyVisitation: null,
        comparingSite: null,
        comparingSiteMonthlyVisitation: null,
        comparingSiteWeeklyVisitation: null,
        dataRange: '',
        chart: null,
        domain: null,
        dateRangeOptions: [
          {text: 'Monthly', value: 'monthly'},
          {text: 'Weekly', value: 'weekly'}
        ]
      }
    },
    methods: {
      _getColors: function(trailName, comparing=false) {
        let colors = {};
        colors[trailName + ' - Modelled'] = comparing ? COLORS.COMPARE_MODELLED : COLORS.MODELLED;
        colors[trailName + ' - On Site'] = comparing ? COLORS.COMPARE_ON_SITE : COLORS.ON_SITE;
        colors[trailName + ' - Flickr'] =  comparing ? COLORS.COMPARE_FLICKR : COLORS.FLICKR;
        colors[trailName + ' - Instagram'] =  comparing ? COLORS.COMPARE_INSTA : COLORS.INSTA;
        colors[trailName + ' - Twitter'] =  comparing ? COLORS.COMPARE_TWITTER : COLORS.TWITTER;
        colors[trailName + ' - WTA'] =  comparing ? COLORS.COMPARE_WTA : COLORS.WTA;
        colors[trailName + ' - AllTrails'] =  comparing ? COLORS.COMPARE_ALLTRAILS : COLORS.ALLTRAILS;
        colors[trailName + ' - eBird'] =  comparing ? COLORS.COMPARE_EBIRD : COLORS.EBIRD;
        colors[trailName + ' - Gravy Analytics'] =  comparing ? COLORS.COMPARE_GRAVY : COLORS.GRAVY;
        colors[trailName + ' - Reveal'] =  comparing ? COLORS.COMPARE_REVEAL : COLORS.REVEAL;
        return colors
      },
      _prepareMonthlyData(trailName, monthlyVisitation, skipDate=false) {
        let self = this;
        let monthlyDates = ['date'];
        let monthlyModelled = [trailName + ' - Modelled'];
        let monthlyOnsite = [trailName + ' - On Site'];
        let monthlyFlickr = [trailName + ' - Flickr'];
        let monthlyInstag = [trailName + ' - Instagram'];
        let monthlyTwitter = [trailName + ' - Twitter'];
        let monthlyWta = [trailName + ' - WTA'];
        let monthlyAllTrails = [trailName + ' - AllTrails'];
        let monthlyeBird = [trailName + ' - eBird'];
        let monthlyGravy = [trailName + ' - Gravy Analytics'];
        let monthlyReveal = [trailName + ' - Reveal'];


        monthlyVisitation.forEach(x => {
          monthlyDates.push(x.year + '-' + x.month + '-1');
          monthlyModelled.push(Math.round(x.estimate, 2));
          monthlyOnsite.push(x.onsite);
          monthlyFlickr.push(x.flickr);
          monthlyInstag.push(x.instag);
          monthlyTwitter.push(x.twitter);
          monthlyWta.push(x.wta);
          monthlyAllTrails.push(x.alltrails);
          monthlyeBird.push(x.ebird);
          monthlyGravy.push(x.gravy);
          monthlyReveal.push(x.reveal);

        });
        const projectDataSources = this.$store.getters.getSelectedProjectDataSources;
        const vizMode = self.$store.getters.getVizMode;

        let timeseriesMonthlyData = [monthlyDates];

        if (projectDataSources.includes('estimate')) {
          timeseriesMonthlyData.push(monthlyModelled);
        }
        if (projectDataSources.includes('onsite') && vizMode !== VIZ_MODES.PROJECT) {
          timeseriesMonthlyData.push(monthlyOnsite);
        }
        if (projectDataSources.includes('flickr')  && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesMonthlyData.push(monthlyFlickr);
        }
        if (projectDataSources.includes('twitter')  && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesMonthlyData.push(monthlyTwitter);
        }
        if (projectDataSources.includes('instag')  && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesMonthlyData.push(monthlyInstag);
        }
        if (projectDataSources.includes('wta')  && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesMonthlyData.push(monthlyWta);
        }
        if (projectDataSources.includes('alltrails')  && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesMonthlyData.push(monthlyAllTrails);
        }
        if (projectDataSources.includes('ebird')  && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesMonthlyData.push(monthlyeBird);
        }
        if (projectDataSources.includes('gravy')  && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesMonthlyData.push(monthlyGravy);
        }
        if (projectDataSources.includes('reveal')  && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesMonthlyData.push(monthlyReveal);
        }
        
        if (skipDate) {
          timeseriesMonthlyData.splice(0, 1)
        }
        return timeseriesMonthlyData
      },
      _prepareWeeklyData(trailName, weeklyVisitation, skipDate=false) {
        let self = this;
        let weeklyDates = ['date'];
        let weeklyModelled = [trailName + ' - Modelled'];
        let weeklyOnsite = [trailName + ' - On Site'];
        let weeklyFlickr = [trailName + ' - Flickr'];
        let weeklyInstag = [trailName + ' - Instagram'];
        let weeklyTwitter = [trailName + ' - Twitter'];
        let weeklyWta = [trailName + ' - WTA'];
        let weeklyAllTrails = [trailName + ' - AllTrails'];
        let weeklyeBird = [trailName + ' - eBird'];
        let weeklyGravy = [trailName + ' - Gravy Analytics'];
        let weeklyReveal = [trailName + ' - Reveal'];


        weeklyVisitation.forEach(x => {
          weeklyDates.push(x.weekstart);
          weeklyModelled.push(Math.round(x.estimate, 2));
          weeklyOnsite.push(x.onsite);
          weeklyFlickr.push(x.flickr);
          weeklyInstag.push(x.instag);
          weeklyTwitter.push(x.twitter);
          weeklyWta.push(x.wta);
          weeklyAllTrails.push(x.alltrails);
          weeklyeBird.push(x.ebird);
          weeklyGravy.push(x.gravy);
          weeklyReveal.push(x.reveal);

        });
        const projectDataSources = self.$store.getters.getSelectedProjectDataSources;
        const vizMode = self.$store.getters.getVizMode;

        let timeseriesWeeklyData = [weeklyDates];

        if (projectDataSources.includes('estimate')) {
          timeseriesWeeklyData.push(weeklyModelled);
        }
        if (projectDataSources.includes('onsite') && vizMode !== VIZ_MODES.PROJECT) {
          timeseriesWeeklyData.push(weeklyOnsite);
        }
        if (projectDataSources.includes('flickr')  && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesWeeklyData.push(weeklyFlickr);
        }
        if (projectDataSources.includes('twitter') && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesWeeklyData.push(weeklyTwitter);
        }
        if (projectDataSources.includes('instag') && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesWeeklyData.push(weeklyInstag);
        }
        if (projectDataSources.includes('wta') && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesWeeklyData.push(weeklyWta);
        }
        if (projectDataSources.includes('alltrails') && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesWeeklyData.push(weeklyAllTrails);
        }
        if (projectDataSources.includes('ebird') && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesWeeklyData.push(weeklyeBird);
        }
        if (projectDataSources.includes('gravy') && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesWeeklyData.push(weeklyGravy);
        }
        if (projectDataSources.includes('reveal') && vizMode !== VIZ_MODES.COMPARE) {
          timeseriesWeeklyData.push(weeklyReveal);
        }

        if (skipDate) {
          timeseriesWeeklyData.splice(0, 1)
        }
        return timeseriesWeeklyData;
      },
      renderTimeSeries: function () {
        let self = this;
        self.loading = true
        if (self.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
          let comparingSiteId = self.$store.getters.getComparingSite['siteid'];
          self.comparingSite = self.$store.getters.getComparingSite;
          axios.all([
            axios.get(this.$apiEndpoint + '/sites/' + comparingSiteId + '/monthlyVisitation'),
            axios.get(this.$apiEndpoint + '/sites/' + comparingSiteId + '/weeklyVisitation')
          ]).then(axios.spread((monthlyVisitationRes, weeklyVisitationRes) => {
            self.comparingSiteMonthlyVisitation = monthlyVisitationRes.data;
            self.comparingSiteWeeklyVisitation = weeklyVisitationRes.data;
            self._renderTimeSeries();
          }))
          .finally(() => {
            this.loading = false
          })
          return
        }

        self.clearTimeSeries();
        this.projectName = self.$store.getters.getSelectedProjectName;
        this.projectCode = self.$store.getters.getSelectedProjectCode;
        this.selectedSite = self.$store.getters.getSelectedSite;
        this.trailName = self.$store.getters.getSelectedSite['trailName'];
        this.siteid = self.$store.getters.getSelectedSite['siteid'];

        let monthlyVisitationUrl, weeklyVisitationUrl;
        if (self.$store.getters.getVizMode === VIZ_MODES.PROJECT) {
          monthlyVisitationUrl = self.$apiEndpoint + '/projects/' + self.projectCode + '/monthlyVisitation';
          weeklyVisitationUrl = self.$apiEndpoint + '/projects/' + self.projectCode + '/weeklyVisitation';
        } else if (self.$store.getters.getVizMode === VIZ_MODES.SITE) {
          monthlyVisitationUrl = self.$apiEndpoint + '/sites/' + self.siteid + '/monthlyVisitation';
          weeklyVisitationUrl = self.$apiEndpoint + '/sites/' + self.siteid + '/weeklyVisitation';
        }

        axios.all([
          axios.get(monthlyVisitationUrl),
          axios.get(weeklyVisitationUrl)
        ]).then(axios.spread((monthlyVisitationRes, weeklyVisitationRes) => {
          self.monthlyVisitation = monthlyVisitationRes.data;
          self.weeklyVisitation = weeklyVisitationRes.data;
          self._renderTimeSeries();
        }))
        .finally(() => {
          this.loading = false
        })
      },
      _renderTimeSeries: function() {
        let self = this;
        self.timeseriesMonthlyData = self._prepareMonthlyData(this.trailName, this.monthlyVisitation);
        self.timeseriesWeeklyData = self._prepareWeeklyData(this.trailName, this.weeklyVisitation);

        let colors = self._getColors(self.trailName);

        if (self.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
          let joinedMonthlyData = self.timeseriesMonthlyData.concat(self._prepareMonthlyData(self.comparingSite['trailName'], self.comparingSiteMonthlyVisitation, true));
          let joinedWeeklyData = self.timeseriesWeeklyData.concat(self._prepareWeeklyData(self.comparingSite['trailName'], self.comparingSiteWeeklyVisitation, true));

          self.timeseriesMonthlyData = joinedMonthlyData;
          self.timeseriesWeeklyData = joinedWeeklyData;

          let compareColors = self._getColors(self.$store.getters.getComparingSite['trailName'], true);
          Object.keys(compareColors).forEach(key => colors[key] = compareColors[key]);
        }

        let data;
        if (self.dataRange === "weekly") {
          data = self.timeseriesWeeklyData
        } else if (self.dataRange === "monthly") {
          data = self.timeseriesMonthlyData
        } else {
          self.dataRange = "monthly";
          data = self.timeseriesMonthlyData
        }
        self.chart = c3.generate({
          bindto: '#time-series',
          data: {
            x: 'date',
            columns: data,
            colors: Object.assign({}, colors)
          },
          axis: {
            x: {
              type: 'timeseries',
              tick: {
                format: function (date) {
                  let x = date.getFullYear() + '-' + (date.getMonth() + 1).pad(2);
                  if (self.dataRange === "monthly") {
                    return x
                  } else if (self.dataRange === "weekly") {
                    return x + '-' + date.getDate().pad(2);
                  }
                },
                rotate: 60,
                fit: false
              }
            },
            y: {
              label: {
                text: 'User-Days',
                position: 'outer-middle'
              }
            }
          },
          zoom: {
            enabled: true,
            rescale: true,
            onzoom: function (domain) {
              self.domain = domain;
            }
          }
        });
      },
      switchDateRange: function() {
        let self = this;
        if (self.dataRange === "monthly") {
          self.chart.load({
            columns: self.timeseriesMonthlyData
          });
        } else if (self.dataRange === "weekly") {
          self.chart.load({
            columns: self.timeseriesWeeklyData
          });
        }
        self.chart.zoom(self.domain);
      },
      clearTimeSeries: function () {
        this.projectName = null;
        this.projectCode = null;
        this.siteid = null;
        this.trailName = null;
        this.selectedSite = null;
        this.monthlyVisitation = null;
        this.weeklyVisitation = null;
        this.comparingSite = null;
        this.comparingSiteMonthlyVisitation = null;
        this.comparingSiteWeeklyVisitation = null;
        this.dataRange = '';
      },
      async downloadData() {
        this.isDownloading = true;
        try {
          const zip = new JSZip();
          const filename = this.getDownloadFilename();
          if (this.timeseriesMonthlyData && this.timeseriesMonthlyData.length > 0) {
            const monthlyCSV = this.convertToCSV(this.timeseriesMonthlyData);
            zip.file(`${filename}_monthly.csv`, monthlyCSV);
          }
          if (this.timeseriesWeeklyData && this.timeseriesWeeklyData.length > 0) {
            const weeklyCSV = this.convertToCSV(this.timeseriesWeeklyData);
            zip.file(`${filename}_weekly.csv`, weeklyCSV);
          }
          const response = await axios.get(this.$apiEndpoint + '/visitation/timeseries/download/readme');
          zip.file('readme.txt', response.data);
          const content = await zip.generateAsync({ type: "blob" });
          FileSaver.saveAs(content, `${filename}.zip`);
        } finally {
          this.isDownloading = false;
        }
      },
      getDownloadFilename: function() {
        const date = new Date();
        const timestamp = `${date.getFullYear()}-${(date.getMonth() + 1).pad(2)}-${date.getDate().pad(2)}`;
        if (this.$store.getters.getVizMode === VIZ_MODES.PROJECT) {
          return `trailtrends_time_series_project_${this.projectCode}_${timestamp}`;
        } else if (this.$store.getters.getVizMode === VIZ_MODES.SITE) {
          return `trailtrends_time_series_site_${this.siteid}_${timestamp}`;
        } else if (this.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
          return `trailtrends_time_series_site_compare_${this.siteid}_${this.comparingSite.siteid}_${timestamp}`;
        }
        return `trails_data_${timestamp}`;
      },
      convertToCSV: function(dataColumns) {
        if (!dataColumns || dataColumns.length === 0) return "";
        const headers = dataColumns.map((col) => col[0]);
        const csvRows = [headers.join(",")];
        const rowCount = dataColumns[0].length - 1; // -1 because first item is header
        for (let i = 1; i <= rowCount; i++) {
          const rowValues = dataColumns.map((col) => col[i] !== undefined ? col[i] : "");
          csvRows.push(rowValues.join(","));
        }
        return csvRows.join("\n");
      },
    },
  };
</script>

<style scoped>
  .time-series-container {
    position: relative; /* ensures the overlay can be placed on top */
    min-height: 50vh;   /* or however tall you want the container to be */
  }

  .disclaimer {
    font-size: 12px;
  }
</style>
