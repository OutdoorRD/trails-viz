<template>
  <h3>{{trailName}}</h3>
</template>

<script>
  import * as d3 from "d3"

  export default {
    name: "BarGraph",
    data: function() {
      return {
        siteid: null,
        trailName: null,
        weeklyEstimates: null,
        monthlyEstimates: null,
        annualEstimates: null
      }
    },
    mounted() {
      let self = this;
    },
    methods: {
      renderBarGraph: function (selectedSite) {
        this.trailName = selectedSite['trailName']
      }

    }
  }
</script>

<style scoped>

</style>
