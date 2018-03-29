(function() {
	'use strict'

	queue()
		.defer(d3.json, "static/data/trails.geojson")
		.await(ready);

	function ready(error, geojsontrails){

		// creates the streets/roads map layer
		var streets = L.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>' +
									' contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
			maxZoom: 18,
			id: 'osm',
		});

		// creates the terrain map layer
		var terrain = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.{ext}', {
			attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>,' +
			 							' <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy;' +
										' <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			maxZoom: 18,
			ext: 'png'
		})

		var baseMaps = {
		    "terrain": terrain,
				"streets": streets
		};

		// sets the initial style for the trails
		var getStyle = function(feature){
			// scale the line thickness to the annual value for each line
			// trial and error led to the formula below
			var weight;
			weight = (feature.properties.annual*0.17)**4

			return {
			color: '#ff7800',
			opacity: 1.0,
			weight: weight
			}
		};

		// highlights a trail that is being hovered over by the user in blue
		var highlightFeature = function(e) {
		    var line = e.target;

		    line.setStyle({
		        weight: 5,
		        color: '#0087ff',
		        opacity: 1.0
		    });

		    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
		        line.bringToFront();
		    }
		};

		// resets the style of a highlighted trail
		var resetHighlight = function(e) {
		    layer.resetStyle(e.target);
		};

		// defines the behavior of the geoJSON trails on the map
		var onEachFeature = function(feature, layer){
			if (feature.properties && feature.properties.Trail_name){
		        layer.bindTooltip(feature.properties.Trail_name);
		        layer.bindPopup(String(feature.properties.annual));
	    }
			layer._leaflet_id = feature.properties.AllTRLs_ID;
	    layer.on({
	    	mouseover: function(e) {
					if(e.target.options.color == "#ff7800") {
						highlightFeature(e);
					}
				},
	    	mouseout: function(e) {
					if (e.target.options.color != "#00ff00") {
						resetHighlight(e)
					}
				},
				click: changeSelect
	    })
		};

		// create geoJSON layer with trail data and defined functionality
		var layer = L.geoJSON(geojsontrails, {
			onEachFeature: onEachFeature,
			style: getStyle
		});

		// create the map variable to be displayed on the website with the default layers
		// shown as the terrain layer and the trail layer
		var map = L.map('trail-map', {
			center: [45, -105],
			zoom: 9,
			layers: [terrain, layer]
		})

		// add map layers, including geoJSON data, to the leaflet map
		L.control.layers(baseMaps).addTo(map);
		layer.addTo(map);
		map.fitBounds(layer.getBounds());

		// changeSelect changes the select box value when a user clicks on a trail
		// on the map and triggers a change event to occur
		function changeSelect() {
			trail_select.value = this._leaflet_id;
			var event = new Event("change");
			trail_select.dispatchEvent(event);
		}

		// the DOM select box to choose a trail
		var trail_select = document.querySelector("#trail-select select");

		// set the initial trail highlighted in green
		var initial_layer = layer.getLayer("5");
		initial_layer.removeFrom(map);
		initial_layer.setStyle({
			weight: 5,
			color: '#00ff00',
			opacity: 1.0
		});
		initial_layer.addTo(map);

		// keep track of the current and previous chosen trails
		var id;
		var previd = 5; // set to the id of the initial layer (Dingford Creek)

		// triggers the map to change when a different trail is selected
		trail_select.onchange = function() {
			updateMap();
		};

		// updateMap highlights the user-selected trail in green on the map and un-highlights the
		// previous trail chosen by the user. If the user re-selects the same trail, nothing
		// happens
		//
		// arguments:
		// 		- select: the DOM select box to choose which trail is shown
		function updateMap() {
			id = trail_select.value;
			console.log(id);
			var newlayer = layer.getLayer(id);
			newlayer.removeFrom(map);
			newlayer.setStyle({
					weight: 5,
					color: '#00ff00',
					opacity: 1.0
			});
			newlayer.addTo(map)
			var prevlayer = layer.getLayer(previd);
			if (previd !== id) {
				prevlayer.setStyle({
					color: '#ff7800',
					opacity: 1.0,
					weight: (prevlayer.feature.properties.annual*0.17)**4
				});
				prevlayer.addTo(map);
				previd = id;
			}
		}

	}

})();
