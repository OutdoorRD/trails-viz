<template>
  <div v-html="compiledMarkdown"></div>
</template>

<script>
  import axios from 'axios'
  import * as marked from 'marked'

  export default {
    name: "InfoViewer",

    data: function () {
      return {
        info: undefined,
        compiledMarkdown: undefined
      }
    },
    methods: {
      renderInfo: function (type) {
        let self = this;
        let url;
        if (type === 'project') {
          let projectCode = self.$store.getters.getSelectedProjectCode;
          url = self.$apiEndpoint + '/projects/' + projectCode + '/readme'
        } else if (type === 'visitation') {
          url = self.$apiEndpoint + '/readme?type=VISITATION_INFO'
        } else if (type === 'homeLocations') {
          url = self.$apiEndpoint + '/readme?type=HOMELOCATIONS_INFO'
        }

        axios.get(url)
          .then(res => {
            self.info = res.data;
            this.compiledMarkdown = marked(this.info)
          });
      }
    }
  }
</script>

<style scoped>

</style>
