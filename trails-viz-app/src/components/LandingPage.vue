<template>
  <div class="landing-page">
    <h1>TrailTrends</h1>
    <h2>Data-driven approaches for mapping outdoor recreation on public lands</h2>

    <p class="form-para">
      <b-form-input list="landing-project-list" placeholder="Type a project name to get started..." autocomplete="off"
                    v-model="projectSearchText" v-on:keyup="autoCompleteProject" v-on:change="routeToDashboard"></b-form-input>

      <b-form-datalist id="landing-project-list" :options="filteredProjects"></b-form-datalist>
    </p>

    <p>
      This dashboard is the result of ongoing collaborations between the
      <a href="https://www.outdoorrd.org" target="_blank">Outdoor Recreation & Data Lab</a>
      at the University of Washington and many partners. The data and results presented here
      are continuously updated and improved. If you have any comments, concerns, or corrections,
      please contact the <a href="https://www.outdoorrd.org/people/" target="_blank">Outdoor R&D Team</a>.
    </p>
    <img :src="bear" alt="Walking bear" class="bear" />
  </div>

</template>

<script>
import bear from "../assets/BearWalking.gif";

  export default {
    name: "LandingPage",
    data: function() {
      return {
        projectSearchText: '',
        filteredProjects: [],
        bear
      }
    },
    mounted() {
      // clear the selected project info
      this.$store.dispatch('clearSelectedProjectData');
    },
    methods: {
      autoCompleteProject: function () {
        let allProjects = this.$store.getters.getAllProjects;
        let projectNames = Object.keys(allProjects);
        let projectNamesUpperCase = projectNames.map(name => name.toUpperCase());

        if (projectNamesUpperCase.includes(this.projectSearchText.toUpperCase())) {
          // don't show suggestions when a valid project is selected
          return
        }
        if (this.projectSearchText.length >= 2) {
          this.filteredProjects = projectNames.filter(name => name.toUpperCase().includes(this.projectSearchText.toUpperCase()));
        } else {
          this.filteredProjects = []
        }
      },
      routeToDashboard: function () {
        if (this.filteredProjects.includes(this.projectSearchText)) {
          this.$store.dispatch('clearSelectedProjectData');

          let selectedProjectCode = this.$store.getters.getAllProjects[this.projectSearchText];

          this.projectSearchText = '';
          this.$router.push({name: 'dashboard', params: {project: selectedProjectCode}});
        }
      }
    }
  }
</script>

<style scoped>

  .landing-page {
    height: calc(100vh - 60px);
    /*background-image: linear-gradient(#17a2b8, #e1f9fc);*/
    background-image: linear-gradient(var(--color-secondary), var(--color-white));
    /* background-color: var(--color-tertiary); */
    align-content: center !important;
    font-family: 'Roboto Condensed', sans-serif;
  }
  h1 {
    font-weight: 700;
    font-size: 75px;
    text-align: center;
    padding: 7.5vh 20vh 4vh 20vh;
    color: var(--color-dark-text);
  }

  h2 {
    font-weight: 500;
    font-size: 40px;
    text-align: center;
    padding: 4vh 12vh 4vh 12vh;
    color: var(--color-dark-text);
  }

  p {
    font-size: large;
    padding: 0 12vh 2vh 12vh;
    color: var(--color-dark-text);
  }

  a {
   color: #2f93a1;
  }

  .form-para {
    margin: 0 200px 0 200px;
  }


  .bear {
  position: absolute;
  bottom: 0;
  left: 0;                       /* anchor at the very left of the container */
  transform: translateX(-100%);  /* shift it left by its own width so it’s fully hidden */
  width: 75px;                  /* or whatever fixed size you like */
  pointer-events: none;
  animation: bear-walk 45s linear infinite;
}

  /* keyframes reference the viewport width + the bear’s own width */
  @keyframes bear-walk {
    /* 0%   */ from { transform: translateX(-100%); }
    /* 100% */ to   { transform: translateX(calc(93vw + 100%)); }
  }

</style>
