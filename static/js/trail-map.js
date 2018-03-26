(function(trailmap) {
	'use strict'

	queue()
		.defer(d3.json, "static/data/trails.geojson")
		.await(ready);

	function ready(error, geojsontrails){
		// leaflet coordinate pairs are always [lat(y), lon(x)] as opposed to [x, y]
		var map = L.map('trail-map').setView([45, -105], 11); 

		var streets = L.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
			maxZoom: 18,
			id: 'osm',
		});//.addTo(map);

		var terrain = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.{ext}', {
			attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			maxZoom: 18,
			ext: 'png'
		}).addTo(map);

		var baseMaps = {
		    "terrain": terrain,
		    "streets": streets
		};

		var getStyle = function(feature){
			// scale the line thickness to the annual value for each line
			// trial and error led to the formula below
			var weight;
			weight = (feature.properties.annual*0.17)**4

			return {
			color: '#ff7800',
			"opacity": 0.95,
			weight: weight
			}
		};

		var onEachFeature = function(feature, layer){
			if (feature.properties && feature.properties.Trail_name) {
		        layer.bindTooltip(feature.properties.Trail_name);
		        layer.bindPopup(feature.properties.Trail_name);
		    }
		};

		// var trailstyle = {
		//     "color": "#ff7800",
		//     "weight": 2,
		//     "opacity": 1.0
		// };

		var layer = L.geoJSON(geojsontrails, {
			onEachFeature: onEachFeature,
			style: getStyle
		});

		L.control.layers(baseMaps).addTo(map);
		layer.addTo(map);
		map.fitBounds(layer.getBounds());
	}

	
}(window.trailmap = window.trailmap || {}));


