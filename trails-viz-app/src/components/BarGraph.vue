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
  import {COLORS, VIZ_MODES} from '../store/constants'
  import c3 from 'c3'
  import axios from 'axios'

  const MONTH_DICT = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'};

  export default {
    name: "BarGraph",
    data: function() {
      return {
        project: null,
        siteid: null,
        trailName: null,
        selectedSite: null,
        monthlyEstimates: null,
        annualEstimates: null,

        comparingSite: null,
        comparingSiteMonthlyEstimates: null,
        comparingSiteAnnualEstimates: null,

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
        let vizMode = self.$store.getters.getVizMode;

        // If mode is compare, fetch the data for comparing sites,
        // render plot and return without overwriting current site data
        if (vizMode === VIZ_MODES.COMPARE) {
          let comparingSiteId = self.$store.getters.getComparingSite['siteid'];
          self.comparingSite = self.$store.getters.getComparingSite;
          axios.all([
            axios.get(self.$apiEndpoint + '/sites/' + comparingSiteId + '/annualEstimates'),
            axios.get(self.$apiEndpoint + '/sites/' + comparingSiteId + '/monthlyEstimates'),
          ]).then(axios.spread((annualEstimateRes, monthlyEstimateRes) => {
            self.comparingSiteAnnualEstimates = annualEstimateRes.data;
            self.comparingSiteMonthlyEstimates = monthlyEstimateRes.data;

            self.renderSelectedGraph();
          }));
          return
        }

        self.clearBarGraph();
        self.project = self.$store.getters.getSelectedProject;
        self.selectedSite = self.$store.getters.getSelectedSite;
        self.trailName = self.$store.getters.getSelectedSite['trailName'];
        self.siteid = self.$store.getters.getSelectedSite['siteid'];

        let annualEstimatesUrl, monthlyEstimatesUrl;
        if (vizMode === VIZ_MODES.PROJECT) {
          annualEstimatesUrl = self.$apiEndpoint + '/projects/' + self.project + '/annualEstimates';
          monthlyEstimatesUrl = self.$apiEndpoint + '/projects/' + self.project + '/monthlyEstimates';
        } else if (vizMode === VIZ_MODES.SITE) {
          annualEstimatesUrl = self.$apiEndpoint + '/sites/' + self.siteid + '/annualEstimates';
          monthlyEstimatesUrl = self.$apiEndpoint + '/sites/' + self.siteid + '/monthlyEstimates'
        }

        axios.all([
          axios.get(annualEstimatesUrl),
          axios.get(monthlyEstimatesUrl)
        ]).then(axios.spread((annualEstimateRes, monthlyEstimateRes) => {
          self.annualEstimates = annualEstimateRes.data;
          self.monthlyEstimates = monthlyEstimateRes.data;

          // on load, render the default graph which is monthly modelled
          if (!self.timePeriod) {
            self.timePeriod = 'monthly';
          }
          if (!self.dataSource) {
            self.dataSource = 'modelled';
          }
          self.renderSelectedGraph();
        }));
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
        if (self.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
          let [compareData, compareColors] = self._prepareMonthlyModelledData(self.comparingSite['trailName'], self.comparingSiteMonthlyEstimates, true);
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
        if (self.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
          let [compareData, compareColors] = self._prepareMonthlySocialMediaData(self.comparingSite['trailName'], self.comparingSiteMonthlyEstimates, true);
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
        if (self.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
          let [compareData, compareColors] = self._prepareAnnualModelledData(self.comparingSite['trailName'], self.comparingSiteAnnualEstimates, true);
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
        if (self.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
          let [compareData, compareColors] = self._prepareAnnualSocialMediaData(self.comparingSite['trailName'], self.comparingSiteAnnualEstimates, true);
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
        this.project = null;
        this.siteid = null;
        this.trailName = null;
        this.selectedSite = null;
        this.monthlyEstimates = null;
        this.annualEstimates = null;
      }
    }
  }
</script>

<style scoped>
  @import "~c3/c3.css";
</style>
