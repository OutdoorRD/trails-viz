<template>
  <div v-html="compiledMarkdown"></div>
</template>

<script>
  import axios from 'axios'
  import * as marked from 'marked'

  export default {
    name: "SiteInfo",

    data: function () {
      return {
        project: undefined,
        projectInfo: undefined,
        compiledMarkdown: undefined
      }
    },
    methods: {
      renderProjectInfo: function () {
        let self = this;
        self.project = self.$store.getters.getSelectedProject;
        axios.get(self.$apiEndpoint + '/projects/' + self.project + '/readme')
          .then(res => {
            self.projectInfo = res.data;
            this.compiledMarkdown = marked(this.projectInfo)
          });
      }
    }
  }
</script>

<style scoped>

</style>
