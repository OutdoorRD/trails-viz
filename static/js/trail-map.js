(function() {
	'use strict'

	queue()
		.defer(d3.json, "static/data/trails.geojson")
		.await(ready);

	function ready(error, geojsontrails){

		var TRAIL_COLOR = '#ff5a3d';
		var SELECTED_COLOR = '#a13dff';
		var TRAIL_OPACITY = 0.75;

		var selected = 1;

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

		// changeSelect changes the checkbox values when a user clicks on a trail
		// on the map and triggers a change event to occur
		// if two trails are already selected, it will reset itself to only have one
		// trail selected
		function changeSelect() {
			var thisid = this._leaflet_id;

			var isSelected = false;
			var input;
			var selectedInputs = [];
			for (var i = 0; i < trail_inputs.length; i++) {
				if (trail_inputs[i].value == thisid && trail_inputs[i].checked) {
					input = trail_inputs[i];
					isSelected = !isSelected;
				} else if (trail_inputs[i].value == thisid) {
					input = trail_inputs[i];
				} else if (trail_inputs[i].checked) {
					selectedInputs.push(trail_inputs[i]);
				}
			}
			if(isSelected) {
				selected--;
				input.checked = !input.checked;
				var event = new Event("change");
				input.dispatchEvent(event);
			} else {
				if (selected == 0 || selected == 1) {
					input.checked = !input.checked;
					selected++;
					var event = new Event("change");
					input.dispatchEvent(event);
				} else {
					var event = new Event("change");
					selected--;
					console.log(selected);
					selectedInputs[0].checked = !selectedInputs[0].checked;
					console.log(selectedInputs[0].checked);
					selectedInputs[0].dispatchEvent(event);
					selectedInputs[1].checked = !selectedInputs[1].checked;
					selectedInputs[1].dispatchEvent(event);
					input.checked = !input.checked;
					input.dispatchEvent(event);
				}
			}
		}

		// array with all the checkbox inputs
		var trail_inputs = document.querySelectorAll("ul.items li input");

		// sets change functionality to all of the input checkboxes
		for (var i = 0; i < trail_inputs.length; i++) {
			trail_inputs[i].onchange = function() { updateMap(); };
		}

		// triggers a change event when the page is loaded for Dingford Creek
		var selectedFirst;
		for (var i = 0; i < trail_inputs.length; i++) {
			if(trail_inputs[i].value == 5) {
				selectedFirst = trail_inputs[i];
				break;
			}
		}
		selectedFirst.dispatchEvent(new Event("change"));

		// set the initial trail highlighted in green
		var initial_layer = layer.getLayer("5");
		initial_layer.removeFrom(map);
		initial_layer.setStyle({
			weight: 5,
			color: SELECTED_COLOR,
			opacity: 1.0
		});
		initial_layer.addTo(map);

		// keeps track of the IDs of the selected trails
		var currIds = [5];

		// updateMap highlights the user-selected trail(s) in purple on the map and un-highlights the
		// trails that have been unselected by the user. If the user re-selects the same trail, it is
		// unselected
		function updateMap() {
			// gets all the IDs of all checked trails
			var checkedIds = [];
			for (var i = 0; i < trail_inputs.length; i++) {
				if (trail_inputs[i].checked) {
					checkedIds.push(trail_inputs[i].value);
				}
			}
			// combines and sorts the checked IDs with the previously current IDs
			var combinedIds = checkedIds.concat(currIds);
			combinedIds = combinedIds.sort();
			var newIds = [];
			// adds duplicate IDs to a variable newIds
			for (var i = 0; i < combinedIds.length - 1; i++) {
				if (combinedIds[i] == combinedIds[i + 1]) {
					newIds.push(combinedIds[i]);
				}
			}
			// removes newIds from currIds to identify which trails need to be
			// unselected
			for (var i = 0; i < newIds.length; i++) {
				for (var j = 0; j < currIds.length; j++) {
					if (newIds[i] == currIds[j]) {
						currIds.splice(j, 1);
						break;
					}
				}
			}
			// unselects trails that aren't selected anymore by using the
			// filtered currIds, which now contains trails that need to be
			// unselected
			for (var i = 0; i < currIds.length; i++) {
				var resetLayer = layer.getLayer(currIds[i]);
				resetLayer.removeFrom(map);
				resetLayer.setStyle({
					color: TRAIL_COLOR,
					opacity: TRAIL_OPACITY,
					weight: (resetLayer.feature.properties.annual*0.17)**4
				});
				resetLayer.addTo(map);
			}
			// selects trails that are checked by matching them with
			// the IDs in checkedIds
			for (var i = 0; i < checkedIds.length; i++) {
				var addLayer = layer.getLayer(checkedIds[i]);
				addLayer.setStyle({
					weight: 5,
					color: SELECTED_COLOR,
					opacity: 1.0
				});
				addLayer.addTo(map);
			}
			// resets currIds to reflect the now-selected trails
			currIds = checkedIds;
		}

	}

})();
