<template>
  <div>
    <div class="map-div" ref="mapDiv"></div>
  </div>
</template>

<script>
  import L from "leaflet";
  import axios from "axios";

  // The following two statements are required because of an issue with leaflet and webpack
  // see https://github.com/Leaflet/Leaflet/issues/4968#issuecomment-483402699
  delete L.Icon.Default.prototype._getIconUrl;

  L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
  });

  const MAPBOX_TOKEN = "pk.eyJ1IjoiZGF2ZW1maXNoIiwiYSI6ImNqZnpvZXNtZzU1bXMzMm52M3g0NDg1NjcifQ.vuO6ajviePMVNbQWd4o3TQ";
  const MAPBOX_TILES_API = "https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}";
  const MAPBOX_ATTRIBUTION = '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © ' +
    '<a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
    '<a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a>';

  export default {
    name: "MapDiv",
    mounted() {
      const mapDiv = L.map(this.$refs["mapDiv"], {
        center: [47, -122],
        zoom: 9
      });

      const outdoorLayer = L.tileLayer(MAPBOX_TILES_API, {
        attribution: MAPBOX_ATTRIBUTION,
        maxZoom: 18,
        id: "mapbox.streets",
        accessToken: MAPBOX_TOKEN
      });

      const satelliteLayer = L.tileLayer(MAPBOX_TILES_API, {
        attribution: MAPBOX_ATTRIBUTION,
        maxZoom: 18,
        id: "mapbox.satellite",
        accessToken: MAPBOX_TOKEN
      });

      L.control.layers({"outdoor": outdoorLayer, "satellite": satelliteLayer}).addTo(mapDiv);
      outdoorLayer.addTo(mapDiv);

      const defaultStyle = {
        color: "#ff0000",
        weight: 0.8
      };

      const siteGroupsGeoJson = {};
      axios
        .get("http://localhost:5000/api/geojson?projectGroup=MBS")
        .then(response => {
          const allSitesGeoJson = response.data;
          mapDiv.fitBounds(L.geoJson(allSitesGeoJson).getBounds());

          for (let feature of allSitesGeoJson["features"]) {
            const siteid = feature["properties"]["siteid"];
            const trailName = feature["properties"]["Trail_name"];

            if (!(siteid in siteGroupsGeoJson)) {
              siteGroupsGeoJson[siteid] = {"type": "FeatureCollection", "name": trailName};
              siteGroupsGeoJson[siteid]["features"] = [];
            }
            siteGroupsGeoJson[siteid]["features"].push(feature);
          }

          Object.entries(siteGroupsGeoJson).forEach(([, site]) => {
            L.geoJSON(site, {style: defaultStyle})
              .bindTooltip(site["name"])
              .addTo(mapDiv);
            }
          )
        })
    }
  }
</script>

<style scoped>
  @import "~leaflet/dist/leaflet.css";
  .map-div {
    height: 800px;
    width: 1000px;
  }
</style>
