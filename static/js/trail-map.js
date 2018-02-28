(function(trailmap) {
	'use strict'

	queue()
		.defer(d3.json, "static/data/trails.geojson")
		.await(ready);

	function ready(error, geojsontrails){
		var map = L.map('trail-map').setView([45, -105], 11); // lat/lon

		// L.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
		// 	attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
		// 	maxZoom: 18,
		// 	id: 'osm',
		// }).addTo(map);

		L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain-background/{z}/{x}/{y}.{ext}', {
			attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			subdomains: 'abcd',
			minZoom: 0,
			maxZoom: 18,
			ext: 'png'
		}).addTo(map);

		var trailstyle = {
		    "color": "#ff7800",
		    "weight": 2,
		    "opacity": 1.0
		};

		var layer = L.geoJSON(geojsontrails, {
			style: trailstyle
		});

		layer.addTo(map);
		map.fitBounds(layer.getBounds());
	}

	
}(window.trailmap = window.trailmap || {}));


