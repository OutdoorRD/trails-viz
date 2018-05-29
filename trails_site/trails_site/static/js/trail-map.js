/*global fetch*/
(function() {
	'use strict'

	queue()
		.defer(d3.json, window.location.href + 'api/geojson')
		.await(ready);

	function ready(error, geojsontrails){

		var TRAIL_COLOR = '#ff5a3d';
		var SELECTED_COLOR = '#a13dff';
		var TRAIL_OPACITY = 0.75;
		var POLYGON_COLOR = '#FF967F';
		var POLYGON_HIGHLIGHT = '#578fff';
		var POLYGON_SELECTED = '#CC8AFF';

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
			"satellite": satellite,
		};

		// var getPolygonStyle = function(feature) {   ///////////////     POLYGON CODE    ////////////////////
		// 	return {
		// 		color: POLYGON_COLOR,
		// 		weight: 2,
		// 		opacity: 0.75
		// 	}
		// }
		//
		// var highlightPolygon = function(e) {
		// 	var polygon;
		// 	if(e.target) {
		// 		polygon = e.target;
		// 	} else {
		// 		polygon = e;
		// 	}
		// 	polygon.setStyle({
		// 		color: POLYGON_HIGHLIGHT,
		// 		weight: 3,
		// 		opacity: 0.75
		// 	});
		// }
		//
		// var resetPolygonHighlight = function(e) {
		// 	trailPolygon.resetStyle(e.target);
		// }
		//
		// var onEachPolygon = function(feature, polylayer) {
		// 	polylayer._leaflet_id = (feature.properties.AllTRLs_ID) + 200;
		// 	polylayer.on({
		// 		mouseover: function(e, feature, polylayer) {
		// 			console.log(polylayer);
		// 			if(e.target.options.color == POLYGON_COLOR) {
		// 				highlightPolygon(e);
		// 				highlightFeature(layer.getLayer(e.target.feature.properties.AllTRLs_ID));
		// 				console.log(e);
		// 			}
		// 		},
		// 		mouseout: function(e, feature, polylayer) {
		// 			if(e.target.options.color != POLYGON_SELECTED) {
		// 				resetPolygonHighlight(e);
		// 				resetHighlight(layer.getLayer(e.target.feature.properties.AllTRLs_ID));
		// 			}
		// 		},
		// 		click: changeSelect
		// 	})
		// }   														///////////		END OF POLYGON CODE    /////////////

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

				// if polygon is being used:
				// var line;
				// if (e.target) {
				// 	line = e.target;
				// } else {
				// 	line = e;
				// }

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

				// if polygon being used:
				// if(e.target) {} else { if(e.options.color != SELECTED_COLOR) {layer.resetStyle(e); } }
		};


		// defines the behavior of the geoJSON trails on the map
		var onEachFeature = function(feature, layer){
			layer.bindTooltip(feature.properties.Trail_name);
			layer._leaflet_id = feature.properties.siteid;
	    layer.on({
	    	mouseover: function(e) {
					if(e.target.options.color == TRAIL_COLOR) {
						highlightFeature(e);
						// if polygon used:
						// highlightPolygon(trailPolygon.getLayer(e.target.feature.properties.siteid + 200));
					}
				},
	    	mouseout: function(e) {
					if (e.target.options.color != SELECTED_COLOR) {
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

		// IF POLYGON BEING USED:
		// var trailPolygon = L.geoJSON(geojsonpolygons, {
		// 	onEachFeature: onEachPolygon,
		// 	style: getPolygonStyle
		// });

		// create the map variable to be displayed on the website with the default layers
		// shown as the outdoor layer and the trail layer
		var map = L.map('trail-map', {
			center: [45, -105],
			zoom: 9,
			layers: [outdoors, layer]  // add trailPolygon if Polygons being used
		});

		// add map layers, including geoJSON data, to the leaflet map
		L.control.layers(baseMaps).addTo(map);
		map.fitBounds(layer.getBounds());

		// changeSelect changes the select box value when a user clicks on a trail
		// on the map and triggers a change event to occur
		function changeSelect() {
			// when a select box is selected, the trail id of that trail is saved in this variable
			var thisid = this._leaflet_id;

			// used for polygons
			if(thisid >= 200) {
				thisid -= 200;
			}

			// adds selected trails to selectedInputs and indicates that the selected trail is checked
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
			// unchecks the selected trail if it is checked (because we are managing a change event, so the
			// trail is supposed to become unchecked)
			// decreases the number of trails selected if the trail isSelected
			if(isSelected) {
				selected--;
				input.checked = !input.checked;
				var event = new Event("change");
				input.dispatchEvent(event);
			// changes the selected value (checks the box)
			// increases the number of selected trails
			// triggers a change event
			} else {
				if (selected == 0 || selected == 1) {
					input.checked = !input.checked;
					selected++;
					var event = new Event("change");
					input.dispatchEvent(event);

				// in this case, two trails have already been selected and we now need to
				// reset it to have one trail selected (because the user is trying to select a third trail)
				} else {
					var event = new Event("change");
					selected--;
					// unchecks the first two trails that are already selected and dispatches a change event
					selectedInputs[0].checked = !selectedInputs[0].checked;
					selectedInputs[0].dispatchEvent(event);
					selectedInputs[1].checked = !selectedInputs[1].checked;
					selectedInputs[1].dispatchEvent(event);
					input.checked = !input.checked;
					// dispatches a change event for the new trail being selected
					input.dispatchEvent(event);
				}
			}
			// toggles the visibility of the social media select boxes so that the user cannot switch
			// them when two trails are selected
			if (selected == 1 || selected == 0) {
				toggleVisibility(true);
			} else {
				toggleVisibility(false);
			}
		}

		var trail_inputs;

		// this interval is run when the page loads so that behavior is not assigned before the dropdown
		// menu has been filled in with trail names
		// once the dropdown is filled, the first trail's data is selected and loaded (i.e. a change event
		// is triggered for Dingford Creek so that data appears when the page loads)
		// the interval is cleared afterwards, so that it doesn't keep running in the background
		var checkForSelect = setInterval(function() {
			if(document.querySelectorAll('#trail-select ul li').length) {
				trail_inputs = document.querySelectorAll('ul.items li input');
				for (var i = 0; i < trail_inputs.length; i++) {
					trail_inputs[i].onchange = function() { updateMap(); };
				}
				var selectedFirst;
				for (var i = 0; i < trail_inputs.length; i++) {
					if (trail_inputs[i].value == 5) {
						selectedFirst = trail_inputs[i];
						break;
					}
				}
				selectedFirst.dispatchEvent(new Event("change"));
				clearInterval(checkForSelect);
			}
		}, 100);



		// set initial trail
		var initial_layer = layer.getLayer("5");
		// var initial_polygon = trailPolygon.getLayer("205");    ///// polygon ///////
		initial_layer.removeFrom(map);
		// initial_polygon.removeFrom(map);				 ///// polygon ///////
		initial_layer.setStyle({
			weight: 5,
			color: SELECTED_COLOR,
			opacity: 1.0
		});
		// initial_polygon.setStyle({						 ///// polygon ///////
		// 	weight: 2,
		// 	color: POLYGON_SELECTED,
		// 	opacity: 0.75
		// });
		// initial_polygon.addTo(map);
		initial_layer.addTo(map);

		// keeps track of the IDs of the selected trails
		// value starts at 5 by default since Dingford Creek is the first trail to be shown
		var currIds = [5];




		// updateMap highlights the user-selected trail in purple on the map and unselects trails that
		// aren't selected anymore by checking trail_inputs
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
				// var resetPolygon = trailPolygon.getLayer(parseInt(currIds[i]) + 200);
				resetLayer.removeFrom(map);
				resetLayer.setStyle({
					color: TRAIL_COLOR,
					opacity: TRAIL_OPACITY,
					weight: (resetLayer.feature.properties.annual*0.17)**4
				});
				// resetPolygon.setStyle({
				// 	color: POLYGON_COLOR,
				// 	opacity: 0.75,
				// 	weight: 2
				// })
				resetLayer.addTo(map);
			}
			// selects trails that are checked by matching them with
			// the IDs in checkedIds
			for (var i = 0; i < checkedIds.length; i++) {
				var addLayer = layer.getLayer(checkedIds[i]);
				// var addPolygon = trailPolygon.getLayer(parseInt(checkedIds[i]) + 200);
				addLayer.setStyle({
					weight: 5,
					color: SELECTED_COLOR,
					opacity: 1.0
				});
				// addPolygon.setStyle({
				// 	weight: 2,
				// 	color: POLYGON_SELECTED,
				// 	opacity: 0.75
				// })
				// addPolygon.addTo(map);
				addLayer.addTo(map);
			}
			// resets currIds to reflect the now-selected trails
			currIds = checkedIds;

		}

	}

	// checks the status of the API fetch and returns a 200 status if okay along with the response
	// text and returns a rejected Promise with an error message if the AJAX call fails
	function checkStatus(response) {
		if (response.status >= 200 && response.status < 300) {
        return response.text();
    } else {
        return Promise.reject(new Error(response.status + ": " + response.statusText));
    }
	}

	// Takes a boolean value 'visible' representing whether
	// the social media  select box should be visible (when one trail is selected)
	// and changes it accordingly
	function toggleVisibility(visible) {
		var social = document.querySelector('.social-select');
		if (visible) {
			social.style.visibility = 'visible';
		} else {
			social.style.visibility = 'hidden';
		}
	}

})();
