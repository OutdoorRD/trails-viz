(function() {
	'use strict'

	queue()
		.defer(d3.json, "static/data/trails.geojson")
		.await(ready);

	function ready(error, geojsontrails){
		// leaflet coordinate pairs are always [lat(y), lon(x)] as opposed to [x, y]
		var map = L.map('trail-map').setView([45, -105], 9);

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
			opacity: 1.0,
			weight: weight
			}
		};

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

		var resetHighlight = function(e) {
		    layer.resetStyle(e.target);
		};

		var onEachFeature = function(feature, layer){
			if (feature.properties && feature.properties.Trail_name){ //&& feature.properties.annual) {
		        layer.bindTooltip(feature.properties.Trail_name);
		        layer.bindPopup(String(feature.properties.annual));
	    }
			layer._leaflet_id = feature.properties.AllTRLs_ID;
	    layer.on({
	    	mouseover: function(e) {
					//console.log(e.target.options.color);
					if(e.target.options.color == "#ff7800") {
						highlightFeature(e);
					}
				},
				//highlightFeature,
	    	mouseout: function(e) {
					//console.log(e.target.options.color);
					if (e.target.options.color != "#00ff00") {
						resetHighlight(e)
					}
				},
				//resetHighlight,
				click: changeSelect
	    })
		};

		var layer = L.geoJSON(geojsontrails, {
			onEachFeature: onEachFeature,
			style: getStyle
		});


		L.control.layers(baseMaps).addTo(map);
		layer.addTo(map);
		map.fitBounds(layer.getBounds());

		function changeSelect() {
			var id = this._leaflet_id;
			console.log("Leaflet id" + id);
			document.querySelector("#trail-select select").value = id;
			var event = new Event("change");
			document.querySelector("#trail-select select").dispatchEvent(event);
		}

		var trail_select = document.querySelector("#trail-select select");
		var id;
		var previd = 5;

		trail_select.onchange = function() {
			logChange(trail_select);
		};

		function logChange(select) {
			id = select.value;
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
