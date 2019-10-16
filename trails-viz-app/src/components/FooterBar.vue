<template>
  <footer>
    <img src="../assets/C3.png" alt="Center for Create Conservation Logo"/>
    <img src="../assets/ForestServiceLogoOfficial.png" alt="Forest Service Official Logo"/>
    <img src="../assets/US-NationalParkService.png" alt="US National Park Service Logo"/>
    <img src="../assets/TNC.png" alt="The Nature Conservancy Logo"/>
    <img src="../assets/natcap.jpg" alt="Natural Capital Project Logo"/>
  </footer>
</template>

<script>
  export default {
    name: "FooterBar"
  }
</script>

<style scoped>
  footer {
    position: absolute;
    width: 100%;
    background-color: lightgray;
    color: white;
    text-align: center;
  }
  footer img {
    padding: 10px 30px 10px 30px;
  }
</style>
