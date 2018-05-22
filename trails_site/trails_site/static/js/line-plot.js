(function(lineplot) {
	'use strict'

	queue()
	//	.defer(d3.csv, "./data/hikers_monthly.csv")
		.defer(d3.json, window.location.href + 'api/hikers_monthly')
		.await(ready);

	function ready(error, hikers_timeseries){


		// var select = d3.select("#trail-select")
	  //     .append("div")
	  //     .append("select")

		var select = d3.select('#trail-select ul');

		select.selectAll("input")
			.data(d3.map(hikers_timeseries, function(d) {
				return d.Trail_name;
			}).values())
			.enter()
			.append('li')
			.append('input')
			.attr("type", "checkbox")
			.attr("value", function(d) { return d.siteid; });

		select.selectAll('li')
			.append('span')
			.text(function(d) {
				return d.Trail_name;
			});

			var list = document.querySelectorAll('ul.items li');
			for (var i = 0; i < list.length; i++) {
				var input = list[i].getElementsByTagName("input")[0];
				if (input.value == "5") {
					input.checked = true;
				}
			}

			var checkList = document.getElementById('list1');
			checkList.getElementsByClassName('anchor')[0].onclick = function(evt) {
				if (checkList.classList.contains('visible')) {
					checkList.classList.remove('visible');
				} else {
					checkList.classList.add('visible');
				}
			}

			sortDropdown();

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


		function changeGraph(d1, value1, d2, value2) {

			var trail_id_1 = value1;

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

				document.getElementById('radioplot1').checked = 'checked';

				var traildata1 = hikers_timeseries.filter(function(d) {
					return (d.siteid == trail_id_1);
				})

				var name1 = traildata1[0].Trail_name;
				document.querySelector('#statistics-info1 #trail-name').innerText = name1;

				var date = [],
					predicted1 = [],
					actual1 = [];

				traildata1.map(function(d) {
					date.push(d.date);
					predicted1.push(+d.estimate);
					actual1.push(+d.onsite);
				});

				predicted1.unshift(traildata1[0].Trail_name + ' - modeled');
				actual1.unshift(traildata1[0].Trail_name + ' - on-site');
				date.unshift('date');

				var plot_data = [];

			if (d2 != null) {

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

					plot_data.push(date, predicted1, actual1, predicted2, actual2);

					fillMonthly(trail_id_1, traildata1[0].Trail_name, trail_id_2, traildata2[0].Trail_name, false);

			} else {

				var flickr = [],
					twitter = [],
					instagram = [],
					wta = [];

				traildata1.map(function(d) {
					flickr.push(+d.flickr);
					twitter.push(+d.twitter);
					instagram.push(+d.instag);
					wta.push(+d.wta);


				});

				flickr.unshift(traildata1[0].Trail_name + ' - Flickr');
				twitter.unshift(traildata1[0].Trail_name + ' - Twitter');
				instagram.unshift(traildata1[0].Trail_name + ' - Instagram');
				wta.unshift(traildata1[0].Trail_name + ' - WTA');

				document.querySelector("#statistics-info2 #trail-name").innerText = "";
				document.querySelector("#statistics-info2 #total-annual-visits").innerText = "";
				document.querySelector("#statistics-info2 #total-summer-visits").innerText = "";
				plot_data.push(date, predicted1, actual1, flickr, twitter, instagram, wta);

				if (document.getElementById('radioplotsocial1').checked) {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, false);
				} else {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, true);
				}

			}

			document.getElementById('radioplotsocial1').onclick = function() {
				if (document.getElementById('radioplot1').checked) {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, false);
				} else {
					fillAnnual(trail_id_1, traildata1[0].Trail_name, null, null, false);
				}
			}

			document.getElementById('radioplotsocial2').onclick = function() {
				if (document.getElementById('radioplot1').checked) {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, true);
				} else {
					fillAnnual(trail_id_1, traildata1[0].Trail_name, null, null, true);
				}
			}

			var social = document.querySelector('.social-select').style;

			document.getElementById('radioplot1').onclick = function() {
				if (d2 != null) {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, trail_id_2, traildata2[0].Trail_name, false);
				} else if(document.getElementById('radioplotsocial1').checked) {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, false);
				} else {
					fillMonthly(trail_id_1, traildata1[0].Trail_name, null, null, true);
				}
			};

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

			var chart = c3.generate({
		    bindto: '#line-plot',
		    data: {
		        x: 'date',
		        xFormat: '%Y-%m', // 'xFormat' can be used as custom format of 'x'
		        columns: plot_data
		    },
				color: {
					pattern: ['#ff595e', '#ffca3a', '#1982c4', '#8ac926', '#6a4c93', '#02c9c2']
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

		} //end changeGraph
	} //end ready function

	function fillMonthly(trailid1, name1, trailid2, name2, social) {
		var bar_data = [];
		var data1, data2;
		fetch(window.location.href + 'api/monthlies/' + trailid1)
			.then(checkStatus)
			.then(JSON.parse)
			.then(function(response) {
				console.log(response);
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

				var sum1 = response[6]['avg_pred'] + response[7]['avg_pred'] + response[8]['avg_pred'];
				var summer1 = document.querySelector("#statistics-info1 #total-summer-visits");
				summer1.innerText = "Average Summer Visits: " + sum1;

				if(trailid2 == null) {
					createMonthly(bar_data);
				} else {
					fetch(window.location.href + 'api/monthlies/' + trailid2)
						.then(checkStatus)
						.then(JSON.parse)
						.then(function(response2) {
							bar_data[1] = [name2 + ' - Average Modeled'];
							for (var i = 0; i < response2.length; i++) {
								bar_data[1].push(response2[i]['avg_pred']);
							}

							var sum2 = response2[6]['avg_pred'] + response2[7]['avg_pred'] + response2[8]['avg_pred'];
							var summer2 = document.querySelector("#statistics-info2 #total-summer-visits");
							summer2.innerText = "Average Summer Visits: " + sum2;

							createMonthly(bar_data);
						})
						.catch(alert);
				}

			})
			.catch(alert);

		//Old fillMonthly
		// console.log(window.location.href + 'api/monthlies/' + id);
		// fetch(window.location.href + 'api/monthlies/' + id)
		// 	.then(checkStatus)
		// 	.then(JSON.parse)
		// 	.then(function(response) {
		// 		generateMonthly(response);
		// 	})
		// 	.catch(alert);
	}

	function fillAnnual(trailid1, name1, trailid2, name2, social) {
		var bar_data = [];

		fetch(window.location.href + 'api/annuals/' + trailid1)
			.then(checkStatus)
			.then(JSON.parse)
			.then(function(response) {
				bar_data[0] = ['Year'];
				if(social) {
					bar_data[1] = ['Flickr'];
					bar_data[2] = ['Twitter'];
					bar_data[3] = ['Instagram'];
					bar_data[4] = ['WTA'];
				} else {
					bar_data[1] = [name1 + ' - Total Annual'];
				}

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
				if (trailid2 == null) {
					createAnnual(bar_data);
				} else {
					fetch(window.location.href + 'api/annuals/' + trailid2)
						.then(checkStatus)
						.then(JSON.parse)
						.then(function(response2) {
							bar_data[2] = [];
							for (var i = 0; i < response2.length; i++) {
								bar_data[2].push(response[i]['avg_pred']);
							}
							createAnnual(bar_data);
						})
						.catch(alert);
				}
			})
			.catch(alert);

		// Old fillAnnual
		// fetch(window.location.href + 'api/annuals/' + id)
		// 	.then(checkStatus)
		// 	.then(JSON.parse)
		// 	.then(function(response) {
		// 		console.log(response);
		// 		generateAnnual(response);
		// 	})
		// 	.catch(alert);
	}

	function createMonthly(bar_data) {
		var colors;
		if (bar_data.length > 2) {
			colors = ['#82cece', '#b7f4ef', '#23b5d3', '#407899'];
		} else {
			colors = ['#ff595e', '#1982c4', '#ffca3a', '#8ac926', '#6a4c93', '#02c9c2'];
		}
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

	function createAnnual(bar_data) {
		var colors;
		if (bar_data.length > 2) {
			colors = ['#82cece', '#b7f4ef', '#23b5d3', '#407899'];
		} else {
			colors = ['#ff595e', '#1982c4', '#ffca3a', '#8ac926', '#6a4c93', '#02c9c2'];
		}
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
