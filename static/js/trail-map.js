(function() {
	'use strict'

	queue()
		.defer(d3.json, "static/data/trails.geojson")
		.await(ready);

	function ready(error, geojsontrails){
		
		var TRAIL_COLOR = '#ff5a3d';
		var SELECTED_COLOR = '#a13dff';
		var TRAIL_OPACITY = 0.75;

		var outdoors = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/outdoors-v9/tiles/256/{z}/{x}/{y}?access_token=' + MAPBOX_TOKEN, {
			attribution:'© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © ' + 
						'<a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
						'<a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a>',
			maxZoom: 18,
			ext: 'png'
		});
		
		var satellite = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v9/tiles/256/{z}/{x}/{y}?access_token=' + MAPBOX_TOKEN, {
			attribution:'© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © ' + 
						'<a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
						'<a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a>',
			maxZoom: 18,
			ext: 'png'
		});

		var baseMaps = {
			"outdoors": outdoors,
			"satellite": satellite
		};

		// sets the initial style for the trails
		var getStyle = function(feature){
			// scale the line thickness to the annual value for each line
			// trial and error led to the formula below
			var weight;
			weight = (feature.properties.annual*0.17)**4

			return {
			color: TRAIL_COLOR,
			opacity: TRAIL_OPACITY,
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
			layer.bindTooltip(feature.properties.Trail_name);
			layer._leaflet_id = feature.properties.AllTRLs_ID;
	    layer.on({
	    	mouseover: function(e, feature, layer) {
					if(e.target.options.color == TRAIL_COLOR) {
						highlightFeature(e);
					}
				},
	    	mouseout: function(e, layer, feature) {
					if (e.target.options.color != SELECTED_COLOR) {
						resetHighlight(e);
					}
				},
				click: changeSelect,
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
			layers: [outdoors, layer]
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
			color: SELECTED_COLOR,
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
					color: SELECTED_COLOR,
					opacity: 1.0
			});
			newlayer.addTo(map)
			var prevlayer = layer.getLayer(previd);
			if (previd !== id) {
				prevlayer.setStyle({
					color: TRAIL_COLOR,
					opacity: TRAIL_OPACITY,
					weight: (prevlayer.feature.properties.annual*0.17)**4
				});
				prevlayer.addTo(map);
				previd = id;
			}
		}

	}

})();
