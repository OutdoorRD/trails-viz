<template>
  <div>
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
  import axios from 'axios'
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
    mounted() {

    },
    methods: {
      renderDefaultGraph: function () {
        let self = this;
        this.trailName = store.selectedSite['trailName'];
        this.siteid = store.selectedSite['siteid'];

        axios.all([
          axios.get(this.$apiEndpoint + '/sites/' + this.siteid + '/annualEstimates'),
          axios.get(this.$apiEndpoint + '/sites/' + this.siteid + '/monthlyEstimates')
        ]).then(axios.spread((annualResponse, monthlyResponse) => {
          self.annualEstimates = annualResponse.data;
          self.monthlyEstimates = monthlyResponse.data;

          self.averageAnnualVisits = self.annualEstimates.map(x => x.estimate).reduce((a, b) => a + b) / self.annualEstimates.length;
          self.averageAnnualVisits = Math.round(self.averageAnnualVisits);

          // on load, render the default graph which is monthly modelled
          if (!self.timePeriod) {
            self.timePeriod = 'monthly';
          }
          if (!self.dataSource) {
            self.dataSource = 'socialMedia';
          }
          self.renderSelectedGraph();
        }));
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
      renderMonthlyModelled: function() {
        let self = this;
        let estimates = ['Monthly Average Modelled'];
        let categories = [];

        self.monthlyEstimates.forEach(x => {
          estimates.push(Math.round(x.estimate));
          categories.push(MONTH_DICT[x.month])
        });
        let data = [estimates];
        self._renderBarGraph(data, categories);
      },
      renderMonthlySocialMedia: function () {
        let self = this;
        let flickr = ['Flickr'];
        let instag = ['Instagram'];
        let twitter = ['Twitter'];
        let wta = ['WTA'];
        let categories = [];

        self.monthlyEstimates.forEach(x => {
          flickr.push(Math.round(x.flickr));
          instag.push(Math.round(x.instag));
          twitter.push(Math.round(x.twitter));
          wta.push(Math.round(x.wta));
          categories.push(MONTH_DICT[x.month])
        });
        let data = [flickr, instag, twitter, wta];
        self._renderBarGraph(data, categories, true);
      },
      renderAnnualModelled: function () {
        let self = this;
        let estimates = ['Annual Modelled'];
        let categories = [];

        self.annualEstimates.forEach(x => {
          estimates.push(Math.round(x.estimate));
          categories.push(x.year)
        });
        let data = [estimates];
        self._renderBarGraph(data, categories);
      },
      renderAnnualSocialMedia: function () {
        let self = this;
        let flickr = ['Flickr'];
        let instag = ['Instagram'];
        let twitter = ['Twitter'];
        let wta = ['WTA'];
        let categories = [];

        self.annualEstimates.forEach(x => {
          flickr.push(Math.round(x.flickr));
          instag.push(Math.round(x.instag));
          twitter.push(Math.round(x.twitter));
          wta.push(Math.round(x.wta));
          categories.push(x.year)
        });
        let data = [flickr, instag, twitter, wta];
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
      }
    }
  }
</script>

<style scoped>
  @import "~c3/c3.css";
</style>
