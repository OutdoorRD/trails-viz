(function(lineplot) {
	'use strict'

	queue()
		.defer(d3.csv, "static/data/hikers_monthly.csv")
		.await(ready);

	function ready(error, hikers_timeseries){

		var select = d3.select("#trail-select ul");

		select.selectAll("input")
			.data(d3.map(hikers_timeseries, function(d) {
				return d.Trail_name;
			}).values())
			.enter()
			.append("li")
			.append("input")
			.attr("type", "checkbox")
			.attr("value", function(d) { return d.AllTRLs_ID; });

		console.log(select.selectAll("li"));

		select.selectAll("li")
			.append("span")
			.text(function(d) {
				return d.Trail_name;
			});

		var list = document.querySelectorAll("ul.items li");
		for (var i = 0; i < list.length; i++) {
			var input = list[i].getElementsByTagName("input")[0];
			if (input.value == "5") {
				input.checked = true;
			}
		}

			var checkList = document.getElementById('list1');
        checkList.getElementsByClassName('anchor')[0].onclick = function (evt) {
            if (checkList.classList.contains('visible'))
                checkList.classList.remove('visible');
            else
                checkList.classList.add('visible');
        };

    // select.on("change", function(d) {
    //     changeGraph(d, d3.select(this).property("value"));
    // });

		var selectedTrails = [];

		var selected = 0;
		var inputs = d3.selectAll("li input");
		inputs.on("change", function(d) {
			if(this.checked == true) {
				if(selected + 1 < 3) {
					selectedTrails.push(this);
					if (selected == 0) {
						changeGraph(d, d3.select(this).property("value"), null, null);
					} else {
						changeGraph(d, d3.select(this).property("value"), d3.select(selectedTrails[0]), d3.select(selectedTrails[0]).property("value"));
					}
					selected++;
				} else {
					this.checked = false;
					alert("A maximum of two trails can be selected at one time");
				}
			} else {
				selected--;
				if(selectedTrails.length == 1 || selectedTrails[0] == this) {
					selectedTrails.shift();
				} else {
					selectedTrails.pop();
				}
				if(selected == 1) {
					changeGraph(d3.select(selectedTrails[0]), d3.select(selectedTrails[0]).property("value"),
										null, null);
				}
			}
		});

		var startgraph = new Event("change");
		var first = document.querySelector("ul li input");
		first.dispatchEvent(startgraph);

/*
some inputs 1 and 2 keep the two possible input data variables

the function to change the graph contains four inputs now -- d1, value1, d2, value2
when a trail is unselected (i.e. going to one trail view), the input containing that
data is cleared and the change graph function is called with d2 and value2 as null parameters
when a trail is selected and selected==0, the function is called again w/ d2 and value2 as null parameters
when a trail is selected and selected==1, the function is called again w/ all function inputs filled


*/



		function changeGraph(d1, value1, d2, value2) {

			var trail_id_1 = value1,
				filename1 = value1 + ".csv";



			// Adds the annual averages statistic to the panel of text about the current trail
			d3.csv("static/data/annuals/" + filename1)
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

			document.getElementById('radioplot2').onclick = function() {
				fillAnnual(filename1);
			};

			var traildata1 = hikers_timeseries.filter(function(d) {
				return (d.AllTRLs_ID == trail_id_1);
			})

			var name1 = traildata1[0].Trail_name;
			document.getElementById('trail-name').innerText = name;

			var date = [],
				predicted1 = [],
				actual1 = [];

			traildata1.map(function(d) {
				date.push(d.date);
				predicted1.push(+d.predicted);
				actual1.push(+d.actual);
			});

			console.log(date);

			predicted1.unshift(traildata1[0].Trail_name + ' - modeled');
			actual1.unshift(traildata1[0].Trail_name + ' - actual');
			date.unshift('date');

			var plot_data = [];

			if (d2 != null) {

				var trail_id_2 = value2,
					filename2 = value2 + ".csv";

				var traildata2 = hikers_timeseries.filter(function(d) {
					return (d.AllTRLs_ID == trail_id_2);
				})

				var predicted2 = [],
					actual2 = [];

				traildata2.map(function(d) {
					predicted2.push(+d.predicted);
					actual2.push(+d.actual);
				})

				predicted2.unshift(traildata2[0].Trail_name + ' - modeled');
				actual2.unshift(traildata2[0].Trail_name + ' - on-site');

				plot_data.push(date, predicted1, actual1, predicted2, actual2);

				fillMonthly(filename1, traildata1[0].Trail_name, filename2, traildata2[0].Trail_name);

			} else {
				plot_data.push(date, predicted1, actual1);
				fillMonthly(filename1, traildata1[0].Trail_name, null, null);
			}

			document.getElementById('radioplot1').onclick = function() {
				if (d2 != null) {
					fillMonthly(filename1, traildata1[0].Trail_name, filename2, traildata2[0].Trail_name);
				} else {
					fillMonthly(filename1, traildata1[0].Trail_name, null, null);
				}
			};

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

			//fillLine(plot_data);
		}


		// Trigger a change event to display data as soon as the page is loaded
		var changeEvent = new Event("change");
		document.querySelector("#trail-select select").value = 5;
		document.querySelector("#trail-select select").dispatchEvent(changeEvent);
}

	function fillLine(plot_data) {
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

	// function fillMonthly(filename) {
	// 	d3.csv("static/data/monthlies/" + filename)
	// 		.row(function(a) {
	// 			console.log(a);
	// 			return [a.avg_pred]; }) // [a.month, a.avg_pred]; })
	// 		.get(function(error, rows) {
	// 			console.log(rows);
	// 			rows.unshift (["Average Modeled"]);// (["Month", "Average Modeled"]);
	//
	// 			// Adds the summary about average summer visits to the panel with text about
	// 			// the current trail
	// 			var sum = parseInt(rows[6]) + parseInt(rows[7]) + parseInt(rows[8]);
	// 			var summer = document.getElementById("total-summer-visits");
	// 			summer.innerText = "Average Summer Visits: " + sum;
	//
	// 			var bar = c3.generate({
	// 					bindto: '#histplot-monthlies-annuals',
	// 					data: {
	// 						rows: rows,
	// 						// x: 'Month',
	// 						type: 'bar'
	// 					},
	// 					axis: {
	// 						x: {
	// 							type: 'category',
	// 							categories: ['Jan', 'Feb', 'March', 'April', 'May', 'June',
	// 														'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
	// 							tick: {
	// 								rotate: 60,
	// 								multiline: false
	// 							},
	// 							height: 40
	// 						},
	// 						y: {
	// 							label: {
	// 								text: 'Average Modeled Number of Visits',
	// 								position: 'outer-middle'
	// 							}
	// 						}
	// 					},
	// 					legend: {
	// 						show: false
	// 					}
	// 			});
	// 		});
	// }

	function fillMonthly(filename1, name1, filename2, name2) {
	  var bar_data = [];
		var data1, data2;
	  d3.csv("static/data/monthlies/" + filename1)
	    .row(function(a) {
	      return [a.avg_pred]; })
	    .get(function(error, rows) {
	      rows.unshift([name1 + " - Average Modeled"]);
				bar_data[0] = [];
				for (var i = 0; i < rows.length; i++) {
					bar_data[0].push(rows[i][0]);
				}
				if (filename2 == null) {
					createMonthly(bar_data);
				}

	      // insert sum data here for trail1 stats info
	      /*
	      var sum = parseInt(rows[6]) + parseInt(rows[7]) + parseInt(rows[8]);
	      var summer = document.getElementById("total-summer-visits");
	      summer.innerText = "Average Summer Visits: " + sum;
	      */
	    });
		if(filename2 !== null) {
		  d3.csv("static/data/monthlies/" + filename2)
		    .row(function(a) { return [a.avg_pred]; })
		    .get(function(error, rows) {
		      rows.unshift([name2 + " - Average Modeled"]);
					bar_data[1] = [];
					console.log(rows);
		      for (var i = 0; i < rows.length; i++) {
						bar_data[1].push(rows[i][0]);
					}
					createMonthly(bar_data);
			});
		console.log(bar_data);
	}
	  // var bar = c3.generate({
	  //   bindto: '#histplot-monthlies-annuals',
	  //   data: {
	  //     rows: bar_data,
	  //     x: 'x',
	  //     type: 'bar'
	  //   },
	  //   axis: {
	  //     x: {
	  //       type: 'category',
	  //       // categories: ['Jan', 'Feb', 'March', 'April', 'May', 'June',
	  //       //               'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
	  //       tick: {
	  //         rotate: 60,
	  //         multiline: false
	  //       },
	  //       height: 40
	  //     },
	  //     y: {
	  //       label: {
	  //         text: 'Average Modeled Number of Visits',
	  //         position: 'outer-middle'
	  //       }
	  //     }
	  //   },
	  //   legend: {
	  //     show: false
	  //   }
	  // });
	}

	function createMonthly(bar_data) {
		var bar = c3.generate({
			bindto: '#histplot-monthlies-annuals',
			data: {
				columns: bar_data,
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
