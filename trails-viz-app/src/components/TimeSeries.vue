<template>
  <div v-show="selectedSite">
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
  import {store} from '../store'
  import c3 from 'c3'

  export default {
    name: "TimeSeries",
    data: function() {
      return {
        siteid: null,
        trailName: null,
        selectedSite: null,
        monthlyVisitation: null,
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
      renderTimeSeries: function () {
        let self = this;
        this.selectedSite = store.selectedSite;
        this.trailName = store.selectedSite['trailName'];
        this.siteid = store.selectedSite['siteid'];
        this.monthlyVisitation = store.monthlyVisitation;
        this.weeklyVisitation = store.weeklyVisitation;

        let monthlyDates = ['date'];
        let monthlyModelled = ['Modelled'];
        let monthlyOnsite = ['On Site'];
        let monthlyFlickr = ['Flickr'];
        let monthlyInstag = ['Instagram'];
        let monthlyTwitter = ['Twitter'];
        let monthlyWta = ['WTA'];

        self.monthlyVisitation.forEach(x => {
          monthlyDates.push(x.year + '-' + x.month + '-1');
          monthlyModelled.push(Math.round(x.estimate, 2));
          monthlyOnsite.push(Math.round(x.onsite, 2));
          monthlyFlickr.push(x.flickr);
          monthlyInstag.push(x.instag);
          monthlyTwitter.push(x.twitter);
          monthlyWta.push(x.wta);
        });
        self.timeseriesMonthlyData = [monthlyDates, monthlyModelled, monthlyOnsite, monthlyFlickr, monthlyInstag, monthlyTwitter, monthlyWta];

        let weeklyDates = ['date'];
        let weeklyModelled = ['Modelled'];
        let weeklyOnsite = ['On Site'];
        let weeklyFlickr = ['Flickr'];
        let weeklyInstag = ['Instagram'];
        let weeklyTwitter = ['Twitter'];
        let weeklyWta = ['WTA'];

        self.weeklyVisitation.forEach(x => {
          let sunday = self._getNthSunday(x.year, x.week);
          weeklyDates.push(x.year + '-' + x.month + '-' + sunday);
          weeklyModelled.push(Math.round(x.estimate, 2));
          weeklyOnsite.push(Math.round(x.onsite, 2));
          weeklyFlickr.push(x.flickr);
          weeklyInstag.push(x.instag);
          weeklyTwitter.push(x.twitter);
          weeklyWta.push(x.wta);
        });
        self.timeseriesWeeklyData = [weeklyDates, weeklyModelled, weeklyOnsite, weeklyFlickr, weeklyInstag, weeklyTwitter, weeklyWta];

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
            columns: data
          },
          axis: {
            x: {
              type: 'timeseries',
              tick: {
                format: '%Y-%m',
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
        this.siteid = null;
        this.trailName = null;
        this.selectedSite = null;
        this.monthlyVisitation = null;
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
