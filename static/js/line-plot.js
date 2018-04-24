(function(lineplot) {
	'use strict'

	queue()
		.defer(d3.csv, "static/data/hikers_monthly.csv")
		.await(ready);

	function ready(error, hikers_timeseries){

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

			// Adds the annual averages statistic to the panel of text about the current trail
			d3.csv("static/data/annuals/" + filename)
				.row(function(a) { return [a.year, a.total_pred]; })
				.get(function(error, rows) {
					var sum = 0;
					for (let i = 0; i < rows.length; i++) {
						var row = rows[i];
						sum += parseInt(row[1]);
					}
					sum = Math.round(sum / rows.length);
					console.log(sum);
					var annual_avg = document.getElementById('total-annual-visits');
					annual_avg.innerText = "Average Annual Visits: " + sum;
				});

			document.getElementById('radioplot1').checked = 'checked';

			document.getElementById('radioplot1').onclick = function() {
				fillMonthly(filename);
			};
			document.getElementById('radioplot2').onclick = function() {
				fillAnnual(filename);
			};

			var traildata = hikers_timeseries.filter(function(d) {
				return (d.AllTRLs_ID == trail_id);
			});

			var traildata2 = hikers_timeseries.filter(function(d) {
				return (d.AllTRLs_ID == "95");
			});

			name = traildata[0].Trail_name;

			// Adds the trail name to the panel of text containing information about the current
			// trail
			document.getElementById('trail-name').innerText = name;

			var date = [],
				predicted = [],
				predicted1 = [],
				actual = [],
				actual1 = [];

			traildata.map(function(d) {
				date.push(d.date);
				predicted.push(+d.predicted);
				actual.push(+d.actual);
			});

			traildata2.map(function(d) {
				predicted1.push(+d.predicted);
				actual1.push(+d.actual);
			});

			console.log(traildata2);

			date.unshift('date');
			predicted.unshift('modeled');
			predicted1.unshift('modeled1');
			actual.unshift('on-site');
			actual1.unshift('on-site1');
			// console.log(date);
			var plot_data = [date, predicted, actual, predicted1, actual1];

			var selected = false;

			var chart = c3.generate({
				bindto: '#line-plot',
				data: {
						x: 'date',
						xFormat: '%Y-%m', // 'xFormat' can be used as custom format of 'x'
						columns: plot_data
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
				},
				legend: {
					item: {
						onclick: function(d) {
							if (selected) {
								// chart.unselect(d);
								// chart.defocus(d);
								chart.revert();
								selected = false;
							} else {
								chart.select(d);
								chart.focus(d);
								selected = true;
							}
						},
						onmouseout: function(d) {
							// prevent deselect on mouseout
						},
						onmouseover: function(d) {

						}
					}
				}
			});

		}

    select.selectAll("option")
      .data(d3.map(hikers_timeseries, function(d){
					//console.log(typeof(d));
					return d.Trail_name;
				})
				.values())
      // .data(hikers_timeseries)
      .enter()
        .append("option")
        .attr("value", function (d) { return d.AllTRLs_ID; })
        .text(function (d) {
					return d.Trail_name; });

		sortDropDown();


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

				// Adds the summary about average summer visits to the panel with text about
				// the current trail
				var sum = parseInt(rows[6]) + parseInt(rows[7]) + parseInt(rows[8]);
				var summer = document.getElementById("total-summer-visits");
				summer.innerText = "Average Summer Visits: " + sum;

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
								categories: ['Jan', 'Feb', 'March', 'April', 'May', 'June',
															'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
								tick: {
									rotate: 60,
									multiline: false
								},
								height: 40
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
							x: {
								tick: {
									rotate: 60,
									multiline: false
								},
								height: 40
							},
							y: {
								label: {
									text: 'Modeled Number of Visits',
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

	function sortDropDown() {
		var dropdown, i, switching, b, shouldSwitch;
		dropdown = document.querySelector('div select');
		switching = true;

		while(switching) {
			switching = false;
			b = dropdown.getElementsByTagName("OPTION");
			for (i = 0; i < (b.length - 1); i++) {
				shouldSwitch = false;
				if (b[i].innerHTML.toLowerCase() > b[i + 1].innerHTML.toLowerCase()) {
					shouldSwitch = true;
					break;
				}
			}
			if (shouldSwitch) {
				b[i].parentNode.insertBefore(b[i + 1], b[i]);
				switching = true;
			}
		}
	}

}(window.lineplot = window.lineplot || {}));
