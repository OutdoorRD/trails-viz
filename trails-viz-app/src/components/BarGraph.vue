<template>
  <div class="bar-graph-container">
    <!-- 1) Loading overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading data...</p>
    </div>
    <b-row no-gutters class="align-items-top justify-content-between mt-2">
  <!-- Radio groups container on the left -->
  <b-col>
    <b-row no-gutters>
      <b-col sm="6">
        <b-form-group>
          <b-radio-group
            v-model="timePeriod"
            :options="timePeriodOptions"
            stacked
            @input="renderSelectedGraph"
          ></b-radio-group>
        </b-form-group>
      </b-col>
      <b-col sm="6">
        <b-form-group>
          <b-radio-group
            v-model="dataSource"
            :options="dataSourceOptions"
            stacked
            @input="renderSelectedGraph"
            :disabled="noEstimates"
          ></b-radio-group>
        </b-form-group>
      </b-col>
    </b-row>
  </b-col>

  <!-- Download button column on the right -->
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

    <b-row no-gutters id="chart-area"></b-row>
  </div>
</template>

<script>
  import {COLORS, VIZ_MODES} from '../store/constants'
  import c3 from 'c3'
  import axios from 'axios'
  import JSZip from "jszip";
  import FileSaver from "file-saver";

  const MONTH_DICT = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'};

  export default {
    name: "BarGraph",
    data: function() {
      return {
        loading: false,
        isDownloading: false,
        projectName: null,
        projectCode: null,
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
        dataSource: '',
        noEstimates: false
      }
    },
    methods: {
      renderDefaultGraph: function () {
        let self = this;
        let vizMode = self.$store.getters.getVizMode;
        self.loading = true
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
          }))
          .finally(() => {
            self.loading = false
          })
          return
        }

        self.clearBarGraph();
        self.projectName = self.$store.getters.getSelectedProjectName;
        self.projectCode = self.$store.getters.getSelectedProjectCode;
        self.selectedSite = self.$store.getters.getSelectedSite;
        self.trailName = self.$store.getters.getSelectedSite['trailName'];
        self.siteid = self.$store.getters.getSelectedSite['siteid'];

        let annualEstimatesUrl, monthlyEstimatesUrl;
        if (vizMode === VIZ_MODES.PROJECT) {
          annualEstimatesUrl = self.$apiEndpoint + '/projects/' + self.projectCode + '/annualEstimates';
          monthlyEstimatesUrl = self.$apiEndpoint + '/projects/' + self.projectCode + '/monthlyEstimates';
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
            // load estimate only when it is a valid data source
            const projectDataSources = self.$store.getters.getSelectedProjectDataSources;
            if (projectDataSources.includes('estimate')) {
              self.dataSource = 'modelled';
            } else {
              self.dataSource = 'socialMedia';
              self.noEstimates = true
            }
          }
          self.renderSelectedGraph();
        }))
        .finally(() => {
          this.loading = false
        })
      },
      _addLabelToArray: function(arr, label) {
        arr.unshift(label);
        return arr;
      },
      _renderBarGraph: function (data, categories, colors, yAxisLabel, showLegend=false) {
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
                text: yAxisLabel,
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
        colors[trailName + ' - AllTrails'] =  comparing ? COLORS.COMPARE_ALLTRAILS : COLORS.ALLTRAILS;
        colors[trailName + ' - eBird'] =  comparing ? COLORS.COMPARE_EBIRD : COLORS.EBIRD;
        colors[trailName + ' - Gravy Analytics'] =  comparing ? COLORS.COMPARE_GRAVY : COLORS.GRAVY;
        colors[trailName + ' - Reveal'] =  comparing ? COLORS.COMPARE_REVEAL : COLORS.REVEAL;

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
        return this._prepareSocialMediaData(trailName, monthlyEstimates, comparing);
      },
      _prepareAnnualSocialMediaData: function(trailName, annualEstimates, comparing=false) {
        return this._prepareSocialMediaData(trailName, annualEstimates, comparing);
      },
      _prepareSocialMediaData: function(trailName, estimates, comparing) {
        let self = this;
        let flickr = [trailName + ' - Flickr'];
        let instag = [trailName + ' - Instagram'];
        let twitter = [trailName + ' - Twitter'];
        let wta = [trailName + ' - WTA'];
        let alltrails = [trailName + ' - AllTrails'];
        let ebird = [trailName + ' - eBird'];
        let gravy = [trailName + ' - Gravy Analytics'];
        let reveal = [trailName + ' - Reveal'];


        estimates.forEach(x => {
          flickr.push(Math.round(x.flickr));
          instag.push(Math.round(x.instag));
          twitter.push(Math.round(x.twitter));
          wta.push(Math.round(x.wta));
          alltrails.push(Math.round(x.alltrails));
          ebird.push(Math.round(x.ebird));
          gravy.push(Math.round(x.gravy));
          reveal.push(Math.round(x.reveal));

        });
        const projectDataSources = self.$store.getters.getSelectedProjectDataSources;
        let socialMediaSources = [];
        if (projectDataSources.includes('flickr')) {
          socialMediaSources.push(flickr);
        }
        if (projectDataSources.includes('instag')) {
          socialMediaSources.push(instag);
        }
        if (projectDataSources.includes('twitter')) {
          socialMediaSources.push(twitter);
        }
        if (projectDataSources.includes('wta')) {
          socialMediaSources.push(wta);
        }
        if (projectDataSources.includes('alltrails')) {
          socialMediaSources.push(alltrails);
        }
        if (projectDataSources.includes('ebird')) {
          socialMediaSources.push(ebird);
        }
        if (projectDataSources.includes('gravy')) {
          socialMediaSources.push(gravy);
        }
        if (projectDataSources.includes('reveal')) {
          socialMediaSources.push(reveal);
        }
        return [socialMediaSources, self._getSocialMediaColors(trailName, comparing)];
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
          self._renderBarGraph(data, categories, colors, 'Average Modeled Number of Visits', true);
        } else {
          self._renderBarGraph(data, categories, colors, 'Average Modeled Number of Visits');
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
        self._renderBarGraph(data, categories, colors, 'Average Social Media User-Days', true);
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
          self._renderBarGraph(data, categories, colors, 'Total Modeled Number of Visits',true);
        } else {
          self._renderBarGraph(data, categories, colors, 'Total Modeled Number of Visits');
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
        self._renderBarGraph(data, categories, colors, 'Total Social Media User-Days', true);
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
        this.projectName = null;
        this.projectCode = null;
        this.siteid = null;
        this.trailName = null;
        this.selectedSite = null;
        this.monthlyEstimates = null;
        this.annualEstimates = null;
      },
      async downloadData() {
        this.isDownloading = true;
        try {
          const zip = new JSZip();
          const filename = this.getDownloadFilename();
          if (this.monthlyEstimates && this.monthlyEstimates.length > 0) {
            // Create a "month" column based on the monthlyEstimates data.
            let monthColumn = ['month'];
            this.monthlyEstimates.forEach(x => {
              monthColumn.push(x.month);
            });
            let [monthlyModelledData] = this._prepareMonthlyModelledData(this.trailName, this.monthlyEstimates);
            if (this.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
              let [compareMonthlyData] = this._prepareMonthlyModelledData(this.comparingSite['trailName'], this.comparingSiteMonthlyEstimates, true);
              monthlyModelledData = monthlyModelledData.concat(compareMonthlyData);
            }
            // Prepend the month column.
            monthlyModelledData.unshift(monthColumn);
            const monthlyModelledCSV = this.convertToCSV(monthlyModelledData);
            zip.file(`${filename}_monthly_modelled.csv`, monthlyModelledCSV);
            let [monthlySocialData] = this._prepareMonthlySocialMediaData(this.trailName, this.monthlyEstimates);
            if (this.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
              let [compareMonthlySocialData] = this._prepareMonthlySocialMediaData(this.comparingSite['trailName'], this.comparingSiteMonthlyEstimates, true);
              monthlySocialData = monthlySocialData.concat(compareMonthlySocialData);
            }
            monthlySocialData.unshift(monthColumn);
            const monthlySocialCSV = this.convertToCSV(monthlySocialData);
            zip.file(`${filename}_monthly_socialMedia.csv`, monthlySocialCSV);
          }

          if (this.annualEstimates && this.annualEstimates.length > 0) {
            // Create a "year" column based on the annualEstimates data.
            let yearColumn = ['year'];
            this.annualEstimates.forEach(x => {
              yearColumn.push(x.year);
            });
            let [annualModelledData] = this._prepareAnnualModelledData(this.trailName, this.annualEstimates);
            if (this.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
              let [compareAnnualData] = this._prepareAnnualModelledData(this.comparingSite['trailName'], this.comparingSiteAnnualEstimates, true);
              annualModelledData = annualModelledData.concat(compareAnnualData);
            }
            // Prepend the year column.
            annualModelledData.unshift(yearColumn);
            const annualModelledCSV = this.convertToCSV(annualModelledData);
            zip.file(`${filename}_annual_modelled.csv`, annualModelledCSV);
            let [annualSocialData] = this._prepareAnnualSocialMediaData(this.trailName, this.annualEstimates);
            if (this.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
              let [compareAnnualSocialData] = this._prepareAnnualSocialMediaData(this.comparingSite['trailName'], this.comparingSiteAnnualEstimates, true);
              annualSocialData = annualSocialData.concat(compareAnnualSocialData);
            }
            annualSocialData.unshift(yearColumn);
            const annualSocialCSV = this.convertToCSV(annualSocialData);
            zip.file(`${filename}_annual_socialMedia.csv`, annualSocialCSV);
          }
          const response = await axios.get(this.$apiEndpoint + '/visitation/bargraph/download/readme');
          zip.file('README.txt', response.data);
          const content = await zip.generateAsync({ type: "blob" });
          FileSaver.saveAs(content, `${filename}.zip`);
        }
        finally {
          this.isDownloading = false;
        }
      },
      getDownloadFilename: function() {
        const date = new Date();
        const timestamp = `${date.getFullYear()}-${(date.getMonth() + 1).pad(2)}-${date.getDate().pad(2)}`;
        if (this.$store.getters.getVizMode === VIZ_MODES.PROJECT) {
          return `trailtrends_bar_graph_project_${this.projectCode}_${timestamp}`;
        } else if (this.$store.getters.getVizMode === VIZ_MODES.SITE) {
          return `trailtrends_bar_graph_site_${this.siteid}_${timestamp}`;
        } else if (this.$store.getters.getVizMode === VIZ_MODES.COMPARE) {
          return `trailtrends_bar_graph_site_compare_${this.siteid}_${this.comparingSite.siteid}_${timestamp}`;
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
  @import "~c3/c3.css";

  .bar-graph-container {
    position: relative;
    min-height: 480px;
  }
</style>
