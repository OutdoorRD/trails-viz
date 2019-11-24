<template>
  <div class="landing-page">
    <h1>Outdoor R&D Trails Visualization Dashboard</h1>

    <p>
      This dashboard is the result of ongoing collaborations between the
      <a href="https://www.outdoorrd.org" target="_blank">Outdoor Recreation & Data Lab</a>
      at the University of Washington and many partners. It would not be possible without
      the support of the US Forest Service, the Department of the Interior,
      Seattle Department of Parks & Recreation, King County Parks & Recreation,
      and many others.
    </p>

    <p>
      The data and models presented here are works in progress, and constantly
      being updated and improved. If you have any comments, concerns, or corrections,
      please reach out to a member of the
      <a href="https://www.outdoorrd.org/people/" target="_blank">Outdoor R&D team</a>.
    </p>

    <p class="form-para">
      <b-form-input list="landing-project-list" placeholder="To get started start typing the project name"
                    v-model="projectSearchText" v-on:keyup="autoCompleteProject" v-on:change="emitProjectNameEvent"></b-form-input>

      <b-form-datalist id="landing-project-list" :options="filteredProjects"></b-form-datalist>
    </p>
    <p class="form-para">
      <small>*Currently supported projects are <i>MBS_PIL</i>, <i>MBS_SARL</i>, and <i>DOI</i></small>.
    </p>

  </div>
</template>

<script>
  export default {
    name: "LandingPage",
    data: function() {
      return {
        projectSearchText: '',
        filteredProjects: []
      }
    },
    methods: {
      scrollToMap: function () {
        document.getElementById("explore").scrollIntoView({behavior: "smooth"});
      },
      autoCompleteProject: function () {
        let store = this.$store;
        if (store.getters.getAllProjects.includes(this.projectSearchText.toUpperCase())) {
          // don't show suggestions when a valid project is selected
          return
        }
        if (this.projectSearchText.length >= 1) {
          this.filteredProjects = store.getters.getAllProjects.filter(name => name.toUpperCase().includes(this.projectSearchText.toUpperCase()));
        } else {
          this.filteredProjects = []
        }
      },
      emitProjectNameEvent: function () {
        if (this.filteredProjects.includes(this.projectSearchText.toUpperCase())) {
          this.$store.dispatch('clearSelectedProjectData');
          this.$store.dispatch('setSelectedProject', this.projectSearchText.toUpperCase());
          this.$emit('project-selected');
          document.getElementById('visualization-zone').scrollIntoView({behavior: "smooth"})
        }
      }
    }
  }
</script>

<style scoped>
  .landing-page {
    /*background-image: linear-gradient(#17a2b8, #e1f9fc);*/
    background-image: linear-gradient(#cce3e3, #ffffff);
    align-content: center !important;
  }
  h1 {
    font-weight: 700;
    font-size: 75px;
    text-align: center;
    padding: 7.5vh 20vh 7.5vh 20vh;
    color: #292f30;
  }

  p {
    font-size: large;
    padding: 0 12vh 2vh 12vh;
  }

  h3 {
    font-weight: 600;
    padding: 0 12vh 0 12vh;
  }

  a {
   color: #2f93a1;
  }

  .form-para {
    margin: 0 200px 0 200px;
  }

</style>
