(function(lineplot) {
	'use strict'

	queue()
		.defer(d3.csv, "static/data/hikers_monthly.csv")
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
			var filename = value + ".csv";

			fillMonthly(filename);
			document.getElementById('radioplot1').checked = 'checked';

			document.getElementById('radioplot1').onclick = function() {
				fillMonthly(filename);
			};
			document.getElementById('radioplot2').onclick = function() {
				fillAnnual(filename);
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
							label: {
								text: 'Number of Visits',
								position: 'outer-middle'
							}
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

	function fillMonthly(filename) {
		d3.csv("static/data/monthlies/" + filename)
			.row(function(a) { return [a.avg_pred]; }) // [a.month, a.avg_pred]; })
			.get(function(error, rows) {
				rows.unshift (["Average Modeled"]);// (["Month", "Average Modeled"]);
				var bar = c3.generate({
						bindto: '#histplot-monthlies-annuals',
						data: {
							rows: rows,
							// x: 'Month',
							type: 'bar'
						},
						axis: {
							x: {
								type: 'category',
								categories: ['January', 'February', 'March', 'April', 'May', 'June',
															'July', 'August', 'September', 'October', 'November', 'December'],
							},
							y: {
								label: {
									text: 'Average Modeled Number of Visits',
									position: 'outer-middle'
								}
							}	
						},
						legend: {
							show: false
						}
				});
			});
	}

	function fillAnnual(filename) {
		d3.csv("static/data/annuals/" + filename)
			.row(function(a) { return [a.year, a.total_pred]; })
			.get(function(error, rows) {
				rows.unshift (["Year", "Total Annual"]);
				var bar = c3.generate({
						bindto: '#histplot-monthlies-annuals',
						data: {
							rows: rows,
							x: 'Year',
							type: 'bar'
						},
						axis: {
							y: {
								label: {
									text: 'Number of visits',
									position: 'outer-middle'
								}
							}
						},
						legend: {
							show: false
						}
				});
			});
	}

}(window.lineplot = window.lineplot || {}));
