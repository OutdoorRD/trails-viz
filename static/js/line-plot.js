(function(lineplot) {
	'use strict'

	queue()
		.defer(d3.csv, "static/data/hikers_monthly.csv")
		.await(ready);

	function ready(error, hikers_monthly){
		console.log(hikers_monthly);

		var select = d3.select("#trail-select")
	      .append("div")
	      .append("select")

	    select
	      .on("change", function(d) {
	        var trail_id = d3.select(this).property("value");
	        console.log(trail_id);

	        var traildata = hikers_monthly.filter(function(d) { return d.AllTRLs_ID == trail_id })
		    console.log(traildata);

		    var date = [],
			    predicted = [],
			    actual = [];
		    
		    traildata.map(function(d) {
			    date.push(d.date);
			    predicted.push(+d.predicted);
			    actual.push(+d.actual);
			})

			date.unshift('date')
			predicted.unshift('predicted')
			actual.unshift('actual')
		    console.log(predicted);

		    var chart = c3.generate({
		    	bindto: '#line-plot',
			    data: {
			        x: 'date',
			        xFormat: '%Y-%m-%d', // 'xFormat' can be used as custom format of 'x'
			        columns: [
			        	date,
			        	predicted,
			        	actual
			            // ['date', '2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04', '2013-01-05', '2013-01-06'],
			            // ['data1', 30, 200, 100, 400, 150, 250],
			            // ['data2', 130, 340, 200, 500, 250, 350]
			        ]
			    },
			    axis: {
			        x: {
			            type: 'timeseries',
			            tick: {
			                format: '%Y-%m-%d'
			            }
			        }
			    },
			     zoom: {
			        enabled: true
			    }
				});

	      });

	    select.selectAll("option")
	      .data(d3.map(hikers_monthly, function(d){return d.Trail_name;}).values())
	      // .data(hikers_monthly)
	      .enter()
	        .append("option")
	        .attr("value", function (d) { return d.AllTRLs_ID; })
	        .text(function (d) { return d.Trail_name; });
		
	}

	
}(window.lineplot = window.lineplot || {}));