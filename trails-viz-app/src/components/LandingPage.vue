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

    <h3>To get started, simply start typing the project name in the search bar.</h3>
    <p>
      Currently supported project names are <i>MBS_PIL</i>, <i>MBS_SARL</i>, and <i>DOI</i>.
      <br/>
      <a href="#explore">Explore</a>
    </p>

  </div>
</template>

<script>
  export default {
    name: "LandingPage"
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

</style>
