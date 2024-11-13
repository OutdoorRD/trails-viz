<template>
  <div>
    <b-row no-gutters>
      <b-col sm="12">
        <b-form-group label="Display Mode">
          <b-form-radio-group v-model="displayMode" @change="renderPartyCharacteristics">
            <b-form-radio value="count">Count</b-form-radio>
            <b-form-radio value="proportion">Proportion</b-form-radio>
          </b-form-radio-group>
        </b-form-group>
      </b-col>
      <b-col sm="12">
        <div id="party-vehicles-chart"></div>
      </b-col>
      <b-col sm="12">
        <div id="party-people-chart"></div>
      </b-col>
      <b-col sm="12">
        <div id="trail-visits-chart"></div>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import c3 from 'c3';
import axios from 'axios';
import { VIZ_MODES } from "../store/constants";

export default {
  name: "PartyCharacteristics",
  data: function () {
    return {
      projectName: null,
      projectCode: null,
      siteid: null,
      partyPeople: null,
      partyVehicles: null,
      trailVisits: null,
      displayMode: 'count' // 'count' or 'proportion'
    };
  },
  methods: {
    renderPartyCharacteristics: function () {
      let self = this;
      let vizMode = self.$store.getters.getVizMode;

      self.projectName = self.$store.getters.getSelectedProjectName;
      self.projectCode = self.$store.getters.getSelectedProjectCode;
      self.siteid = self.$store.getters.getSelectedSite['siteid'];

      let endpoints = {
        partyVehicles: vizMode === VIZ_MODES.PROJECT
          ? `${self.$apiEndpoint}/projects/${self.projectCode}/partyVehicles`
          : `${self.$apiEndpoint}/sites/${self.siteid}/partyVehicles`,
        trailVisits: vizMode === VIZ_MODES.PROJECT
          ? `${self.$apiEndpoint}/projects/${self.projectCode}/trailVisits`
          : `${self.$apiEndpoint}/sites/${self.siteid}/trailVisits`,
        partyPeople: vizMode === VIZ_MODES.PROJECT
          ? `${self.$apiEndpoint}/projects/${self.projectCode}/partyPeople`
          : `${self.$apiEndpoint}/sites/${self.siteid}/partyPeople`
      };

      Promise.all([
        axios.get(endpoints.partyVehicles),
        axios.get(endpoints.trailVisits),
        axios.get(endpoints.partyPeople)
      ])
      .then(([partyVehiclesResponse, trailVisitsResponse, partyPeopleResponse]) => {
        this.partyVehicles = partyVehiclesResponse.data;
        this.trailVisits = trailVisitsResponse.data;
        this.partyPeople = partyPeopleResponse.data;
        // Render all charts at once
        this._makePartyVehiclesChart(this.partyVehicles);
        this._makeTrailVisitsChart(this.trailVisits);
        this._makePartyPeopleChart(this.partyPeople);
      });
    },
    _makePartyVehiclesChart: function (partyVehicles) {
      let data = {
        '0 Vehicles': 0,
        '1 Vehicle': 0,
        '2 Vehicles': 0,
        '3+ Vehicles': 0
      };
      for (const x of partyVehicles) {
        if (x['PartyVehics'] >= 3) {
          data['3+ Vehicles'] += 1;
        } else if (x['PartyVehics'] === 2) {
          data['2 Vehicles'] += 1;
        } else if (x['PartyVehics'] === 1) {
          data['1 Vehicle'] += 1;
        } else {
          data['0 Vehicles'] += 1;
        }
      }
      this._makeBarChart(data, '#party-vehicles-chart', 'Party Vehicles');
    },

    _makePartyPeopleChart: function (partyPeople) {
      let data = {
        '0 People': 0,
        '1 Person': 0,
        '2 People': 0,
        '3+ People': 0
      };
      for (const x of partyPeople) {
        if (x['PartyPeople'] >= 3) {
          data['3+ People'] += 1;
        } else if (x['PartyPeople'] === 2) {
          data['2 People'] += 1;
        } else if (x['PartyPeople'] === 1) {
          data['1 Person'] += 1;
        } else {
          data['0 People'] += 1;
        }
      }
      this._makeBarChart(data, '#party-people-chart', 'Party People');
    },

    _makeTrailVisitsChart: function (trailVisitsData) {
      let data = {
        '0 Visits': 0,
        '1 Visit': 0,
        '2 Visits': 0,
        '3+ Visits': 0
      };
      for (const x of trailVisitsData) {
        if (x['TrailVisits'] >= 3) {
          data['3+ Visits'] += 1;
        } else if (x['TrailVisits'] === 2) {
          data['2 Visits'] += 1;
        } else if (x['TrailVisits'] === 1) {
          data['1 Visit'] += 1;
        } else {
          data['0 Visits'] += 1;
        }
      }
      this._makeBarChart(data, '#trail-visits-chart', 'Trail Visits');
    },

    _makeBarChart: function (data, htmlElemId, title) {
      let categories = Object.keys(data);
      let values = Object.values(data);

      if (this.displayMode === 'proportion') {
        const total = values.reduce((sum, val) => sum + val, 0);
        values = total > 0
          ? values.map(val => ((val / total) * 100).toFixed(2))
          : values.map(() => 0); // Set all to 0 if total is 0
        values.unshift('Proportion (%)');
      } else {
        values.unshift('Count');
      }

      c3.generate({
        bindto: htmlElemId,
        size: {
          height: 200
        },
        axis: {
          x: {
            type: 'category',
            categories: categories,
            label: {
              text: title,
              position: 'outer-center'
            },
            tick: {
              multiline: false
            },
            height: 40
          },
          y: {
            label: {
              text: this.displayMode === 'proportion' ? 'Proportion (%)' : 'Count',
              position: 'outer-middle'
            }
          }
        },
        legend: {
          show: false
        },
        data: {
          columns: [values],
          type: 'bar'
        },
        tooltip: {
          format: {
            value: function (value) {
              return value === 'Proportion (%)' ? '0%' : value; // Ensure tooltip shows 0% for all zeros
            }
          }
        }
      });
    }

  },
  mounted() {
    this.renderPartyCharacteristics();
  }
};
</script>

<style scoped>
#party-vehicles-chart, #party-people-chart, #trail-visits-chart {
  padding: 10px;
}
</style>
