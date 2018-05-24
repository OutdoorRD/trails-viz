(function(lineplot) {
	'use strict'

	queue()
	//	.defer(d3.csv, "./data/hikers_monthly.csv")
		.defer(d3.json, window.location.href + 'api/hikers_monthly')
		.await(ready);

	function ready(error, hikers_timeseries){

		var select = d3.select('#trail-select ul');

		// adds trail checkboxes to the header
		select.selectAll("input")
			.data(d3.map(hikers_timeseries, function(d) {
				return d.Trail_name;
			}).values())
			.enter()
			.append('li')
			.append('input')
			.attr("type", "checkbox")
			.attr("value", function(d) { return d.siteid; });

		// adds list elements to the header to display the trail name in the dropdown
		select.selectAll('li')
			.append('span')
			.text(function(d) {
				return d.Trail_name;
			});

			// sets an initial trail to be selected
			var list = document.querySelectorAll('ul.items li');
			for (var i = 0; i < list.length; i++) {
				var input = list[i].getElementsByTagName("input")[0];
				if (input.value == "5") {
					input.checked = true;
				}
			}

			// defines the visibility of the checklist (drops down when clicked)
			var checkList = document.getElementById('list1');
			checkList.getElementsByClassName('anchor')[0].onclick = function(evt) {
				if (checkList.classList.contains('visible')) {
					checkList.classList.remove('visible');
				} else {
					checkList.classList.add('visible');
				}
			}

			// sorts the dropdown alphabetically
			sortDropdown();

			// contains trails currently selected
			var selectedTrails = [];

			// allows for a maximum of 2 trails to be selected at once
			// triggers change functions when a new trail is selected
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

		// changes the graphs on the page according to what has been selected by the user
		function changeGraph(d1, value1, d2, value2) {

			// first trail's siteid
			var trail_id_1 = value1;

			// adds average annual visits for trail 1 to the page by fetching the data from the annual API
			fetch(window.location.href + 'api/annuals/' + trail_id_1)
				.then(checkStatus)
				.then(JSON.parse)
				.then(function(response) {
					var sum = 0;
					for (var i = 0; i < response.length; i++) {
						sum += response[i]['avg_pred'];
					}
					sum = Math.round(sum / response.length);
					var annual_avg = document.querySelector('#statistics-info1 #total-annual-visits');
					annual_avg.innerText = "Average Annual Visits: " + sum;
				})
				.catch(alert);

				// sets the monthly checkbox to be selected first
				document.getElementById('radioplot1').checked = 'checked';

				// filters the overall trail data for data on trail 1
				var traildata1 = hikers_timeseries.filter(function(d) {
					return (d.siteid == trail_id_1);
				})

				// gets name of trail 1 and fills the page accordingly
				var name1 = traildata1[0].Trail_name;
				document.querySelector('#statistics-info1 #trail-name').innerText = name1;

				// variables for the dates and predicted/actual values for trail 1
				var date = [],
					predicted1 = [],
					actual1 = [];

				// adds trail 1 date, estimate, and onsite values to the arrays
				traildata1.map(function(d) {
					date.push(d.date);
					predicted1.push(+d.estimate);
					actual1.push(+d.onsite);
				});

				// adds titles to the arrays with the information for use in graphing
				predicted1.unshift(traildata1[0].Trail_name + ' - modeled');
				actual1.unshift(traildata1[0].Trail_name + ' - on-site');
				date.unshift('date');

				// variable that gets passed to the line plot
				var plot_data = [];

				// if a second trail is selected
			if (d2 != null) {
				// repeat the above process using the second trail selected
				var trail_id_2 = value2;

				var traildata2 = hikers_timeseries.filter(function(d) {
					return (d.siteid == trail_id_2);
				});

				var name2 = traildata2[0].Trail_name;
				document.querySelector("#statistics-info2 #trail-name").innerText = name2;

				fetch(window.location.href + 'api/annuals/' + trail_id_2)
					.then(checkStatus)
					.then(JSON.parse)
					.then(function(response) {
						var sum = 0;
						for (var i = 0; i < response.length; i++) {
							sum += response[i]['avg_pred'];
						}
						sum = Math.round(sum / response.length);
						var annual_avg = document.querySelector('#statistics-info2 #total-annual-visits');
						annual_avg.innerText = "Average Annual Visits: " + sum;
					})
					.catch(alert);

					var predicted2 = [],
						actual2 = [];

					traildata2.map(function(d) {
						predicted2.push(+d.estimate);
						actual2.push(+d.onsite);
					});

					predicted2.unshift(traildata2[0].Trail_name + ' - modeled');
					actual2.unshift(traildata2[0].Trail_name + ' - on-site');

					// add all of the modeled and on-site data to the array being passed to the line plot
					plot_data.push(date, predicted1, actual1, predicted2, actual2);

					// fill the monthly bar chart with information on the two trails
					fillMonthly(trail_id_1, traildata1[0].Trail_name, trail_id_2, traildata2[0].Trail_name, false);

			} else { // only one trail is selected

				// define arrays for the social media data
				var flickr = [],
					twitter = [],
					instagram = [],
					wta = [];

				// add social media data to the variables
				traildata1.map(function(d) {
					flickr.push(+d.flickr);
					twitter.push(+d.twitter);
					instagram.push(+d.instag);
					wta.push(+d.wta);
				});

				// add titles for the variables for the bar chart to use
				flickr.unshift(traildata1[0].Trail_name + ' - Flickr');
				twitter.unshift(traildata1[0].Trail_name + ' - Twitter');
				instagram.unshift(traildata1[0].Trail_name + ' - Instagram');
				wta.unshift(traildata1[0].Trail_name + ' - WTA');

				// Clear the trail2 statistics
				document.querySelector("#statistics-info2 #trail-name").innerText = "";
				document.querySelector("#statistics-info2 #total-annual-visits").innerText = "";
				document.querySelector("#statistics-info2 #total-summer-visits").innerText = "";

				// Add social media data as well as modeled and onsite data to the plot data variable
				plot_data.push(date, predicted1, actual1, flickr, twitter, instagram, wta);

				// If social media is selected then the monthly bar chart with social media data
				// is plotted and if not, the onsite and modeled bar chart is plotted
				if (document.getElementById('radioplotsocial1').checked) {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, false);
				} else {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, true);
				}

			}

			// changes the bar chart when social media is changed (shows annual or monthly depending
			// on what is currently selected)
			document.getElementById('radioplotsocial1').onclick = function() {
				if (document.getElementById('radioplot1').checked) {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, false);
				} else {
					fillAnnual(trail_id_1, traildata1[0].Trail_name, null, null, false);
				}
			}

			// changes the bar chart when social media option is chaanged (shows annual or monthly depending
			// on what is currently selected)
			document.getElementById('radioplotsocial2').onclick = function() {
				if (document.getElementById('radioplot1').checked) {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, true);
				} else {
					fillAnnual(trail_id_1, traildata1[0].Trail_name, null, null, true);
				}
			}

			// puts the social media selection div's style in a variable so it can easily be hidden
			var social = document.querySelector('.social-select').style;

			// changes bar chart to monthly data
			document.getElementById('radioplot1').onclick = function() {
				if (d2 != null) {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, trail_id_2, traildata2[0].Trail_name, false);
				} else if(document.getElementById('radioplotsocial1').checked) {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, false);
				} else {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, true);
				}
			};

			// changes bar chart to annual data
			document.getElementById('radioplot2').onclick = function() {
				if (d2 != null) {
					fillAnnual(trail_id_1, traildata1[0].Trail_name, trail_id_2, traildata2[0].Trail_name, false);
				} else if (document.getElementById('radioplotsocial1').checked) {
					fillAnnual(trail_id_1, traildata1[0].Trail_name, null, null, false);
				} else {
					fillAnnual(trail_id_1, traildata1[0].Trail_name, null, null, true);
				}
			};

			var selected = false;

			// creates the annual line plot using plot_data
			var chart = c3.generate({
		    bindto: '#line-plot',
		    data: {
		        x: 'date',
		        xFormat: '%Y-%m', // 'xFormat' can be used as custom format of 'x'
		        columns: plot_data
		    },
				// custom color pattern that matches the bar chart when social media data not shown
				color: {
					pattern: ['#ff595e', '#ffca3a', '#1982c4', '#8ac926', '#6a4c93', '#02c9c2']
				},
		    axis: {
		        x: {
		            type: 'timeseries',
		            tick: {
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
						// defines behavior for when you click on the legend
						// and want to the other lines to fade out
		        onclick: function(d) {
		          if (selected) {
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
							// prevent select on mouseover
		        }
		      }
		    }
		  });

		} //end changeGraph

	} //end ready function

	// Fills the bar chart with monthly data.
	// Parameters required:
	// 	- trailid1 = the siteid of the first trail you are plotting
	// 	- name1 = the name of the first trail you are plotting
	// 	- trailid2 = the siteid of the second trail you are plotting
	// 	- name2 = the name of the secodn trail you are plotting
	// 	- social = boolean value representing whether or not you wish to display social media data
	// note: social should only be true when trailid2 and name2 are false
	// note: if trailid2 and name2 are null, only one trail's data is plotted
	function fillMonthly(trailid1, name1, trailid2, name2, social) {
		var bar_data = [];
		var data1, data2;
		// calls the monthlies API and parses JSON data returned
		fetch(window.location.href + 'api/monthlies/' + trailid1)
			.then(checkStatus)
			.then(JSON.parse)
			.then(function(response) {
				// fills bar_data based on whether or not social media is selected
				bar_data[0] = [];
				if(social) {
					bar_data[0].push('Flickr');
					bar_data[1] = ['Twitter'];
					bar_data[2] = ['Instagram'];
					bar_data[3] = ['WTA'];
				} else { bar_data[0].push(name1 + ' - Average Modeled'); }
				for (var i = 0; i < response.length; i++) {
					if (social) {
						bar_data[0].push(response[i]['flickr']);
						bar_data[1].push(response[i]['twitter']);
						bar_data[2].push(response[i]['instag']);
						bar_data[3].push(response[i]['wta']);
					} else {
						bar_data[0].push(response[i]['avg_pred']);
					}
				}

				// fills in the rest of the statistics information
				var sum1 = response[6]['avg_pred'] + response[7]['avg_pred'] + response[8]['avg_pred'];
				var summer1 = document.querySelector("#statistics-info1 #total-summer-visits");
				summer1.innerText = "Average Summer Visits: " + sum1;

				// if a second trail is not selected, creates the monthly bar chart
				// otherwise, gets second trail data
				if(trailid2 == null) {
					createMonthly(bar_data);
				} else {
					// fetch second trail data and parse JSON
					fetch(window.location.href + 'api/monthlies/' + trailid2)
						.then(checkStatus)
						.then(JSON.parse)
						.then(function(response2) {
							// add the modeled data from trail 2 to the bar chart data
							bar_data[1] = [name2 + ' - Average Modeled'];
							for (var i = 0; i < response2.length; i++) {
								bar_data[1].push(response2[i]['avg_pred']);
							}

							// fill in statistics for trail 2
							var sum2 = response2[6]['avg_pred'] + response2[7]['avg_pred'] + response2[8]['avg_pred'];
							var summer2 = document.querySelector("#statistics-info2 #total-summer-visits");
							summer2.innerText = "Average Summer Visits: " + sum2;

							// create monthly bar chart that contains both trails' data
							createMonthly(bar_data);
						})
						.catch(alert);
				}

			})
			.catch(alert);

	} // end fillMonthly

	// Fills the bar chart with annual data.
	// Parameters required:
	// 	- trailid1 = the siteid of the first trail you are plotting
	// 	- name1 = the name of the first trail you are plotting
	// 	- trailid2 = the siteid of the second trail you are plotting
	// 	- name2 = the name of the secodn trail you are plotting
	// 	- social = boolean value representing whether or not you wish to display social media data
	// note: social should only be true when trailid2 and name2 are false
	// note: if trailid2 and name2 are null, only one trail's data is plotted
	function fillAnnual(trailid1, name1, trailid2, name2, social) {
		var bar_data = [];

		// calls the annual API and parses JSON data returned
		fetch(window.location.href + 'api/annuals/' + trailid1)
			.then(checkStatus)
			.then(JSON.parse)
			.then(function(response) {
				// creates arrays corresponding to year and social media or modeled data depending on
				// whether or not social media is selected
				bar_data[0] = ['Year'];
				if(social) {
					bar_data[1] = ['Flickr'];
					bar_data[2] = ['Twitter'];
					bar_data[3] = ['Instagram'];
					bar_data[4] = ['WTA'];
				} else {
					bar_data[1] = [name1 + ' - Total Annual'];
				}

				// fills in yea and predicted/social media data to the bar_data
				for (var i = 0; i < response.length; i++) {
					bar_data[0].push(response[i]['year']);
					if (social) {
						bar_data[1].push(response[i]['flickr']);
						bar_data[2].push(response[i]['twitter']);
						bar_data[3].push(response[i]['instag']);
						bar_data[4].push(response[i]['wta']);
					} else {
						bar_data[1].push(response[i]['avg_pred'])
					}
				}
				// creates the annual bar chart if one trail is selected
				if (trailid2 == null) {
					createAnnual(bar_data);
				} else {
					// fetches the second trail's annual data and parses the JSON in the response text
					fetch(window.location.href + 'api/annuals/' + trailid2)
						.then(checkStatus)
						.then(JSON.parse)
						.then(function(response2) {
							// adds trail 2 data to the bar_data variable
							bar_data[2] = [];
							for (var i = 0; i < response2.length; i++) {
								bar_data[2].push(response[i]['avg_pred']);
							}
							// creates the annual bar chart with both trails' data
							createAnnual(bar_data);
						})
						.catch(alert);
				}
			})
			.catch(alert);
	} // end fillAnnual

	// creates the monthly bar chart
	function createMonthly(bar_data) {
		var colors;
		// if bar data contains social media information, uses a different color combination
		if (bar_data.length > 2) {
			colors = ['#82cece', '#b7f4ef', '#23b5d3', '#407899'];
		} else {
			// this color combination will match the line plot when two trails are selected
			colors = ['#ff595e', '#1982c4', '#ffca3a', '#8ac926', '#6a4c93', '#02c9c2'];
		}
		// generates the bar chart
		var bar = c3.generate({
			bindto: '#histplot-monthlies-annuals',
			data: {
				columns: bar_data,
				type: 'bar'
			},
			color: {
				pattern: colors
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

	// creates the annual bar chart
	function createAnnual(bar_data) {
		var colors;
		// selects custom colors based on social media data or two trails
		if (bar_data.length > 2) {
			colors = ['#82cece', '#b7f4ef', '#23b5d3', '#407899'];
		} else {
			colors = ['#ff595e', '#1982c4', '#ffca3a', '#8ac926', '#6a4c93', '#02c9c2'];
		}
		// creates annual bar chart 
		var bar = c3.generate({
				bindto: '#histplot-monthlies-annuals',
				data: {
					columns: bar_data,
					x: 'Year',
					type: 'bar'
				},
				color: {
					pattern: colors
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

	// Sorts the dropdown select menu to be alphabetized
	function sortDropdown() {
		var dropdown, i, switching, b, shouldSwitch;
		dropdown = document.querySelector('div ul');
		switching = true;

		while(switching) {
			switching = false;
			b = dropdown.getElementsByTagName("LI");
			for (i = 0; i < (b.length - 1); i++) {
				shouldSwitch = false;
				var input1 = b[i].getElementsByTagName("SPAN");
				var input2 = b[i + 1].getElementsByTagName("SPAN");
				if (input1[0].innerHTML.toLowerCase() > input2[0].innerHTML.toLowerCase()) {
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
