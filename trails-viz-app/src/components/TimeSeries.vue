<template>
  <div>
    <b-row no-gutters>
      <b-col class="text-right">
        <b-form-group>
          <b-radio-group v-model="dataRange" :options="dateRangeOptions" v-on:input="switchDateRange"></b-radio-group>
        </b-form-group>
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

  Number.prototype.pad = function (size) {
    let s = String(this);
    while (s.length < (size || 2)) {s = "0" + s;}
    return s;
  };

  export default {
    name: "TimeSeries",
    data: function() {
      return {
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
      _getNthSunday: function(year, n) {
        let date = new Date(year, 0);
        let firstSunday;
        if (date.getDay() === 0) {
          firstSunday = date.getDate();
        } else {
          firstSunday = date.getDate() + 7 - date.getDay()
        }
        let dayOfYear = (n - 1) * 7 + firstSunday;
        date.setDate(dayOfYear);
        return date.getDate();
      },
      _getColors: function(trailName, comparing=false) {
        let colors = {};
        colors[trailName + ' - Modelled'] = comparing ? COLORS.COMPARE_MODELLED : COLORS.MODELLED;
        colors[trailName + ' - On Site'] = comparing ? COLORS.COMPARE_ON_SITE : COLORS.ON_SITE;
        colors[trailName + ' - Flickr'] =  comparing ? COLORS.COMPARE_FLICKR : COLORS.FLICKR;
        colors[trailName + ' - Instagram'] =  comparing ? COLORS.COMPARE_INSTA : COLORS.INSTA;
        colors[trailName + ' - Twitter'] =  comparing ? COLORS.COMPARE_TWITTER : COLORS.TWITTER;
        colors[trailName + ' - WTA'] =  comparing ? COLORS.COMPARE_WTA : COLORS.WTA;
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

        monthlyVisitation.forEach(x => {
          monthlyDates.push(x.year + '-' + x.month + '-1');
          monthlyModelled.push(Math.round(x.estimate, 2));
          monthlyOnsite.push(x.onsite);
          monthlyFlickr.push(x.flickr);
          monthlyInstag.push(x.instag);
          monthlyTwitter.push(x.twitter);
          monthlyWta.push(x.wta);
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

        weeklyVisitation.forEach(x => {
          let sunday = self._getNthSunday(x.year, x.week);
          weeklyDates.push(x.year + '-' + x.month + '-' + sunday);
          weeklyModelled.push(Math.round(x.estimate, 2));
          weeklyOnsite.push(x.onsite);
          weeklyFlickr.push(x.flickr);
          weeklyInstag.push(x.instag);
          weeklyTwitter.push(x.twitter);
          weeklyWta.push(x.wta);
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

        if (skipDate) {
          timeseriesWeeklyData.splice(0, 1)
        }
        return timeseriesWeeklyData;
      },
      renderTimeSeries: function () {
        let self = this;

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
          }));
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
        }));
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
            xFormat: '%Y-%m-%d', // 'xFormat' can be used as custom format of 'x'
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
                text: 'Number of Visits',
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
      }
    }
  }
</script>

<style scoped>
  .disclaimer {
    font-size: 12px;
  }
</style>
