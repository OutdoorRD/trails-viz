(function(lineplot) {
	'use strict'

	queue()
	//	.defer(d3.csv, "./data/hikers_monthly.csv")
		.defer(d3.json, window.location.href + 'api/hikers_monthly')
		.await(ready);

	function ready(error, hikers_timeseries){

		console.log(hikers_timeseries);

		var select = d3.select("#trail-select")
	      .append("div")
	      .append("select")

    select.on("change", function(d) {
        changeGraph(d, d3.select(this).property("value"));
    });


		function changeGraph(d, value) {
			var trail_id = value;
			// console.log(trail_id);
			// var filename = value + ".csv";

			fillMonthly(trail_id);
			document.getElementById('radioplot1').checked = 'checked';

			document.getElementById('radioplot1').onclick = function() {
				fillMonthly(trail_id);
			};
			document.getElementById('radioplot2').onclick = function() {
				fillAnnual(trail_id);
			};

			var traildata = hikers_timeseries.filter(function(d) { return d.AllTRLs_ID == trail_id })

			var date = [],
				predicted = [],
				actual = [];

			traildata.map(function(d) {
				date.push(d.date);
				predicted.push(+d.predicted);
				actual.push(+d.actual);
			})

			date.unshift('date')
			predicted.unshift('modeled')
			actual.unshift('on-site')
			// console.log(date);

			var chart = c3.generate({
				bindto: '#line-plot',
				data: {
						x: 'date',
						xFormat: '%Y-%m', // 'xFormat' can be used as custom format of 'x'
						columns: [
							date,
							predicted,
							actual
						]
				},
				axis: {
						x: {
								type: 'timeseries',
								tick: {
									// culling: {max: 6},
										format: '%Y-%m',
										fit: false
								}
						},
						y: {
							label: 'Number of Visits'
						}
				},
				 zoom: {
						enabled: true
				}
			});
		}

    select.selectAll("option")
      .data(d3.map(hikers_timeseries, function(d){return d.Trail_name;}).values())
      // .data(hikers_timeseries)
      .enter()
        .append("option")
        .attr("value", function (d) { return d.AllTRLs_ID; })
        .text(function (d) { return d.Trail_name; });

		// Trigger a change event to display data as soon as the page is loaded
		var changeEvent = new Event("change");
		document.querySelector("#trail-select select").value = 5;
		document.querySelector("#trail-select select").dispatchEvent(changeEvent);
	}

	function fillMonthly(id) {
		console.log(window.location.href + 'api/monthlies/' + id);
		fetch(window.location.href + 'api/monthlies/' + id)
			.then(checkStatus)
			.then(JSON.parse)
			.then(function(response) {
				generateMonthly(response);
			})
			.catch(alert);
	}

	function fillAnnual(id) {
		fetch(window.location.href + 'api/annuals/' + id)
			.then(checkStatus)
			.then(JSON.parse)
			.then(function(response) {
				generateAnnual(response);
			})
			.catch(alert);
	}

	function generateMonthly(data) {
		var bar = c3.generate({
			bindto: '#histplot-monthlies-annuals',
			data: {
				json: data,
				keys: {
					value: ['avg_pred']
				},
				type: 'bar'
			},
			axis: {
				x: {
					type: 'category',
					categories: ['January', 'February', 'March', 'April', 'May', 'June',
					 							'July', 'August', 'September', 'October', 'November', 'December']
				},
				y: {
					label: 'Average Modeled Number of Visits'
				}
			}
		});
	}

	function generateAnnual(data) {
		var bar = c3.generate({
			bindto: '#histplot-monthlies-annuals',
			data: {
				json: data,
				keys: {
					x: 'year',
					value: ['avg_pred']
				},
				type: 'bar'
			},
			axis: {
				y: {
					label: 'Number of visits'
				}
			}
		});
	}

	function checkStatus(response) {
		if (response.status >= 200 && response.status < 300) {
        return response.text();
    } else {
        return Promise.reject(new Error(response.status + ": " + response.statusText));
    }
	}

}(window.lineplot = window.lineplot || {}));
