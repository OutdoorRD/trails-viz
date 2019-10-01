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
        monthlyVisitation: null
      }
    },
    methods: {
      renderTimeSeries: function () {
        let self = this;
        this.selectedSite = store.selectedSite;
        this.trailName = store.selectedSite['trailName'];
        this.siteid = store.selectedSite['siteid'];
        this.monthlyVisitation = store.monthlyVisitation;

        let dates = ['date'];
        let modelled = ['Modelled'];
        let onsite = ['On Site'];
        let flickr = ['Flickr'];
        let instag = ['Instagram'];
        let twitter = ['Twitter'];
        let wta = ['WTA'];

        self.monthlyVisitation.forEach(x => {
          dates.push(x.year + '-' + x.month);
          modelled.push(Math.round(x.estimate, 2));
          onsite.push(Math.round(x.onsite, 2));
          flickr.push(x.flickr);
          instag.push(x.instag);
          twitter.push(x.twitter);
          wta.push(x.wta);
        });
        let timeseriesData = [dates, modelled, onsite, flickr, instag, twitter, wta];

        c3.generate({
          bindto: '#time-series',
          data: {
            x: 'date',
            xFormat: '%Y-%m', // 'xFormat' can be used as custom format of 'x'
            columns: timeseriesData
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
            enabled: true
          }
        });
      }
    }
  }
</script>

<style scoped>
  .disclaimer {
    font-size: 12px;
  }
</style>
