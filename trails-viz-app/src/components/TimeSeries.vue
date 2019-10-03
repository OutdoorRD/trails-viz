<template>
  <div v-show="selectedSite">
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
        dataRange: ''
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
        let timeseriesMonthlyData = [monthlyDates, monthlyModelled, monthlyOnsite, monthlyFlickr, monthlyInstag, monthlyTwitter, monthlyWta];

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
        let timeseriesWeeklyData = [weeklyDates, weeklyModelled, weeklyOnsite, weeklyFlickr, weeklyInstag, weeklyTwitter, weeklyWta];

        self.dataRange = 'monthly';
        let chart = c3.generate({
          bindto: '#time-series',
          data: {
            x: 'date',
            xFormat: '%Y-%m-%d', // 'xFormat' can be used as custom format of 'x'
            columns: timeseriesMonthlyData
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
              let startDate = domain[0];
              let endDate = domain[1];
              let diffTime = Math.abs(endDate - startDate);
              let diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
              if (self.dataRange === 'monthly' && diffDays <= 500) {
                self.dataRange = 'weekly';
                chart.load({
                  columns: timeseriesWeeklyData
                });
                chart.zoom(domain);
              } else if (self.dataRange === 'weekly' && diffDays > 500) {
                self.dataRange = 'monthly';
                chart.load({
                  columns: timeseriesMonthlyData
                });
                chart.zoom(domain);
              }
            }
          }
        });
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
