(function(trailmap) {
	'use strict'

	queue()
		.defer(d3.json, "static/data/trails.geojson")
		.await(ready);

	function ready(error, geojsontrails){
		var map = L.map('trail-map').setView([45, -105], 11); // lat/lon

		L.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
			maxZoom: 18,
			id: 'osm',
		}).addTo(map);

		var trailstyle = {
		    "color": "#ff7800",
		    "weight": 1,
		    "opacity": 1.0
		};

		var layer = L.geoJSON(geojsontrails, {
			style: trailstyle
		});

		layer.addTo(map);
		map.fitBounds(layer.getBounds());
	}

	
}(window.trailmap = window.trailmap || {}));


