<template>
  <div>
    <div v-if="loading">
      Loading, please wait...
    </div>
    <p v-else v-html="compiledMarkdown"></p>
  </div>
</template>

<script>
  import axios from 'axios'
  import * as marked from 'marked'

  export default {
    name: "InfoViewer",

    data: function () {
      return {
        info: undefined,
        compiledMarkdown: undefined,
        loading: false
      }
    },
    methods: {
      renderInfo: function (type) {
        this.loading = true
        let self = this;
        let url;
        let projectCode = self.$store.getters.getSelectedProjectCode;
        if (type === 'project') {
          url = self.$apiEndpoint + '/projects/' + projectCode + '/readme?type=INFO'
        } else if (type === 'visitation') {
          url = self.$apiEndpoint + '/projects/' + projectCode + '/readme?type=VISITS'
        } else if (type === 'homeLocations') {
          url = self.$apiEndpoint + '/readme?type=HOMELOCATIONS_INFO'
        }

        axios.get(url)
          .then(res => {
            self.info = res.data;
            this.compiledMarkdown = marked(this.info)
          })
          .catch(() => {
          })
          .finally(() => {
            this.loading = false
          })
      }
    }
  }
</script>

<style scoped>
  p {
    height: 75vh;
    overflow: auto;
  }
</style>
