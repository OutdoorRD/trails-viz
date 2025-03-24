<template>
  <div class="info-viewer-container">
    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading data...</p>
    </div>

    <!-- Markdown Content -->
    <div v-else class="markdown-content" v-html="compiledMarkdown"></div>
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
    computed: {
      selectedSource() {
        return this.$store.getters.getSelectedSource;
      },
      visibleTabGroup() {
        return this.$store.getters.getVisibleTabGroup;
      }
    },
    watch: {
      selectedSource() {
        if (this.visibleTabGroup === 'visitorCharacteristics') {
          this.renderInfo('homeLocations');
        }
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
          url = self.$apiEndpoint + '/datasources/' + this.selectedSource + '/readme'
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
  .info-viewer-container {
    position: relative;
    min-height: 75vh; /* Enough height so overlay covers the entire area */
  }
 
</style>
