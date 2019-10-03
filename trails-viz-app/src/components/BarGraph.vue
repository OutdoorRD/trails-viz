<template>
  <div v-show="selectedSite">
    <b-row no-gutters>
      <b-col>
        <h3>{{trailName}}</h3>
        <p>Average Annual Visits: <b>{{averageAnnualVisits}}</b></p>
      </b-col>
    </b-row>
    <b-row no-gutters>
      <b-col sm="6">
        <b-form-group>
          <b-radio-group v-model="timePeriod" :options="timePeriodOptions" stacked v-on:input="renderSelectedGraph"></b-radio-group>
        </b-form-group>
      </b-col>
      <b-col sm="6">
        <b-form-group>
          <b-radio-group v-model="dataSource" :options="dataSourceOptions" stacked v-on:input="renderSelectedGraph"></b-radio-group>
        </b-form-group>
      </b-col>
    </b-row>
    <b-row no-gutters id="chart-area"></b-row>
  </div>
</template>

<script>
  import {store} from '../store'
  import c3 from 'c3'

  const MONTH_DICT = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'};

  export default {
    name: "BarGraph",
    data: function() {
      return {
        siteid: null,
        trailName: null,
        selectedSite: null,
        weeklyEstimates: null,
        monthlyEstimates: null,
        annualEstimates: null,
        averageAnnualVisits: '',

        timePeriodOptions: [
          {text: 'Annual', value: 'annual'},
          {text: 'Monthly', value: 'monthly'}
        ],
        dataSourceOptions: [
          {text: 'Modelled', value: 'modelled'},
          {text: 'Social Media', value: 'socialMedia'}
        ],
        timePeriod: '',
        dataSource: ''
      }
    },
    methods: {
      renderDefaultGraph: function () {
        let self = this;
        this.selectedSite = store.selectedSite;
        this.trailName = store.selectedSite['trailName'];
        this.siteid = store.selectedSite['siteid'];

        self.annualEstimates = store.annualEstimates;
        self.monthlyEstimates = store.monthlyEstimates;

        self.averageAnnualVisits = self.annualEstimates.map(x => x.estimate).reduce((a, b) => a + b) / self.annualEstimates.length;
        self.averageAnnualVisits = Math.round(self.averageAnnualVisits);

        // on load, render the default graph which is monthly modelled
        if (!self.timePeriod) {
          self.timePeriod = 'monthly';
        }
        if (!self.dataSource) {
          self.dataSource = 'modelled';
        }
        self.renderSelectedGraph();
      },
      _addLabelToArray: function(arr, label) {
        arr.unshift(label);
        return arr;
      },
      _renderBarGraph: function (data, categories, showLegend=false) {
        c3.generate({
          bindto: '#chart-area',
          size: {
            height: 480
          },
          axis: {
            x: {
              type: 'category',
              categories: categories,
              tick: {
                rotate: 60,
                multiline: false
              },
              height: 40
            },
            y: {
              label: {
                text: 'Average Modeled Number of Visits',
                position: 'outer-middle'
              }
            }
          },
          legend: {
            show: showLegend
          },
          data: {
            columns: data,
            type: 'bar'
          }
        })
      },
      _prepareMonthlyModelledData: function(trailName, monthlyEstimates) {
        let estimates = [trailName + ' - Monthly Average Modelled'];
        monthlyEstimates.forEach(x => {
          estimates.push(Math.round(x.estimate));
        });
        return [estimates];
      },
      _prepareAnnualModelledData: function(trailName, annualEstimates) {
        let estimates = [trailName + ' - Annual Modelled'];
        annualEstimates.forEach(x => {
          estimates.push(Math.round(x.estimate));
        });
        return [estimates];
      },
      _prepareMonthlySocialMediaData: function(trailName, monthlyEstimates) {
        let flickr = [trailName + ' - Flickr'];
        let instag = [trailName + ' - Instagram'];
        let twitter = [trailName + ' - Twitter'];
        let wta = [trailName + ' - WTA'];

        monthlyEstimates.forEach(x => {
          flickr.push(Math.round(x.flickr));
          instag.push(Math.round(x.instag));
          twitter.push(Math.round(x.twitter));
          wta.push(Math.round(x.wta));
        });
        return [flickr, instag, twitter, wta];
      },
      _prepareAnnualSocialMediaData: function(trailName, annualEstimates) {
        let flickr = [trailName + ' - Flickr'];
        let instag = [trailName + ' - Instagram'];
        let twitter = [trailName + ' - Twitter'];
        let wta = [trailName + ' - WTA'];

        annualEstimates.forEach(x => {
          flickr.push(Math.round(x.flickr));
          instag.push(Math.round(x.instag));
          twitter.push(Math.round(x.twitter));
          wta.push(Math.round(x.wta));
        });
        return [flickr, instag, twitter, wta];
      },
      renderMonthlyModelled: function() {
        let self = this;
        let categories = [];
        self.monthlyEstimates.forEach(x => {
          categories.push(MONTH_DICT[x.month])
        });
        let data = self._prepareMonthlyModelledData(self.trailName, self.monthlyEstimates);
        if (store.comparingSite) {
          data = data.concat(self._prepareMonthlyModelledData(store.comparingSite['trailName'], store.comparingSiteMonthlyEstimates));
        }
        self._renderBarGraph(data, categories);
      },
      renderMonthlySocialMedia: function () {
        let self = this;
        let categories = [];

        self.monthlyEstimates.forEach(x => {
          categories.push(MONTH_DICT[x.month])
        });
        let data = self._prepareMonthlySocialMediaData(self.trailName, self.monthlyEstimates);
        if (store.comparingSite) {
          data = data.concat(self._prepareMonthlySocialMediaData(store.comparingSite['trailName'], store.comparingSiteMonthlyEstimates));
        }
        self._renderBarGraph(data, categories, true);
      },
      renderAnnualModelled: function () {
        let self = this;
        let categories = [];

        self.annualEstimates.forEach(x => {
          categories.push(x.year)
        });
        let data = self._prepareAnnualModelledData(self.trailName, self.annualEstimates);
        if (store.comparingSite) {
          data = data.concat(self._prepareAnnualModelledData(store.comparingSite['trailName'], store.comparingSiteAnnualEstimates));
        }
        self._renderBarGraph(data, categories);
      },
      renderAnnualSocialMedia: function () {
        let self = this;
        let categories = [];

        self.annualEstimates.forEach(x => {
          categories.push(x.year)
        });
        let data = self._prepareAnnualSocialMediaData(self.trailName, self.annualEstimates);
        if (store.comparingSite) {
          data = data.concat(self._prepareAnnualSocialMediaData(store.comparingSite['trailName'], store.comparingSiteMonthlyEstimates));
        }
        self._renderBarGraph(data, categories, true);
      },
      renderSelectedGraph: function () {
        if (this.timePeriod === 'monthly' && this.dataSource === 'modelled') {
          this.renderMonthlyModelled()
        } else if (this.timePeriod === 'monthly' && this.dataSource === 'socialMedia') {
          this.renderMonthlySocialMedia()
        } else if (this.timePeriod === 'annual' && this.dataSource === 'modelled') {
          this.renderAnnualModelled()
        } else if (this.timePeriod === 'annual' && this.dataSource === 'socialMedia') {
          this.renderAnnualSocialMedia()
        }
      },
      clearBarGraph: function () {
        this.siteid = null;
        this.trailName = null;
        this.selectedSite = null;
        this.weeklyEstimates = null;
        this.monthlyEstimates = null;
        this.annualEstimates = null;
        this.averageAnnualVisits = '';
        this.timePeriod = '';
        this.dataSource = '';
      }
    }
  }
</script>

<style scoped>
  @import "~c3/c3.css";
</style>
