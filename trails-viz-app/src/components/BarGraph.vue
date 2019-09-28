<template>
  <h3>{{trailName}}</h3>
</template>

<script>
  import {store} from '../store'

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

    },
    methods: {
      renderBarGraph: function () {
        this.trailName = store.selectedSite['trailName']
      }
    }
  }
</script>

<style scoped>

</style>
