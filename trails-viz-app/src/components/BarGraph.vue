<template>
  <div>
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
  import {COLORS} from '../store/constants'
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
        this.selectedSite = self.$store.getters.getSelectedSite;
        this.trailName = self.$store.getters.getSelectedSite['trailName'];
        this.siteid = self.$store.getters.getSelectedSite['siteid'];

        self.annualEstimates = self.$store.getters.getAnnualEstimates;
        self.monthlyEstimates = self.$store.getters.getMonthlyEstimates;

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
      _renderBarGraph: function (data, categories, colors, showLegend=false) {
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
            type: 'bar',
            colors: Object.assign({}, colors) // clone the object to avoid side effects as c3 updates this object on it's own
          }
        })
      },
      _getSocialMediaColors:  function(trailName, comparing) {
        let colors = {};
        colors[trailName + ' - Flickr'] =  comparing ? COLORS.COMPARE_FLICKR : COLORS.FLICKR;
        colors[trailName + ' - Instagram'] =  comparing ? COLORS.COMPARE_INSTA : COLORS.INSTA;
        colors[trailName + ' - Twitter'] =  comparing ? COLORS.COMPARE_TWITTER : COLORS.TWITTER;
        colors[trailName + ' - WTA'] =  comparing ? COLORS.COMPARE_WTA : COLORS.WTA;
        return colors;
      },
      _prepareMonthlyModelledData: function(trailName, monthlyEstimates, comparing=false) {
        let estimates = [trailName + ' - Monthly Average Modelled'];
        let colors = {};
        monthlyEstimates.forEach(x => {
          estimates.push(Math.round(x.estimate));
        });
        colors[trailName + ' - Monthly Average Modelled'] =  comparing ? COLORS.COMPARE_MODELLED : COLORS.MODELLED;
        return [[estimates], colors];
      },
      _prepareAnnualModelledData: function(trailName, annualEstimates, comparing=false) {
        let estimates = [trailName + ' - Annual Modelled'];
        let colors = {};
        annualEstimates.forEach(x => {
          estimates.push(Math.round(x.estimate));
        });
        colors[trailName + ' - Annual Modelled'] =  comparing ? COLORS.COMPARE_MODELLED : COLORS.MODELLED;
        return [[estimates], colors];
      },
      _prepareMonthlySocialMediaData: function(trailName, monthlyEstimates, comparing=false) {
        let self = this;
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

        return [[flickr, instag, twitter, wta], self._getSocialMediaColors(trailName, comparing)];
      },
      _prepareAnnualSocialMediaData: function(trailName, annualEstimates, comparing=false) {
        let self = this;
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
        return [[flickr, instag, twitter, wta], self._getSocialMediaColors(trailName, comparing)];
      },
      renderMonthlyModelled: function() {
        let self = this;
        let categories = [];
        self.monthlyEstimates.forEach(x => {
          categories.push(MONTH_DICT[x.month])
        });
        let [data, colors] = self._prepareMonthlyModelledData(self.trailName, self.monthlyEstimates);
        if (self.$store.getters.getComparingSite) {
          let [compareData, compareColors] = self._prepareMonthlyModelledData(self.$store.getters.getComparingSite['trailName'], self.$store.getters.getComparingSiteMonthlyEstimates, true);
          data = data.concat(compareData);
          Object.keys(compareColors).forEach(key => colors[key] = compareColors[key]);
          self._renderBarGraph(data, categories, colors, true);
        } else {
          self._renderBarGraph(data, categories, colors);
        }

      },
      renderMonthlySocialMedia: function () {
        let self = this;
        let categories = [];

        self.monthlyEstimates.forEach(x => {
          categories.push(MONTH_DICT[x.month])
        });
        let [data, colors] = self._prepareMonthlySocialMediaData(self.trailName, self.monthlyEstimates);
        if (self.$store.getters.getComparingSite) {
          let [compareData, compareColors] = self._prepareMonthlySocialMediaData(self.$store.getters.getComparingSite['trailName'], self.$store.getters.getComparingSiteMonthlyEstimates, true);
          data = data.concat(compareData);
          Object.keys(compareColors).forEach(key => colors[key] = compareColors[key]);
        }
        self._renderBarGraph(data, categories, colors, true);
      },
      renderAnnualModelled: function () {
        let self = this;
        let categories = [];

        self.annualEstimates.forEach(x => {
          categories.push(x.year)
        });
        let [data, colors] = self._prepareAnnualModelledData(self.trailName, self.annualEstimates);
        if (self.$store.getters.getComparingSite) {
          let [compareData, compareColors] = self._prepareAnnualModelledData(self.$store.getters.getComparingSite['trailName'], self.$store.getters.getComparingSiteAnnualEstimates, true);
          data = data.concat(compareData);
          Object.keys(compareColors).forEach(key => colors[key] = compareColors[key]);
          self._renderBarGraph(data, categories, colors, true);
        } else {
          self._renderBarGraph(data, categories, colors);
        }
      },
      renderAnnualSocialMedia: function () {
        let self = this;
        let categories = [];

        self.annualEstimates.forEach(x => {
          categories.push(x.year)
        });
        let [data, colors] = self._prepareAnnualSocialMediaData(self.trailName, self.annualEstimates);
        if (self.$store.getters.getComparingSite) {
          let [compareData, compareColors] = self._prepareAnnualSocialMediaData(self.$store.getters.getComparingSite['trailName'], self.$store.getters.getComparingSiteMonthlyEstimates, true);
          data = data.concat(compareData);
          Object.keys(compareColors).forEach(key => colors[key] = compareColors[key]);
        }
        self._renderBarGraph(data, categories, colors, true);
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
