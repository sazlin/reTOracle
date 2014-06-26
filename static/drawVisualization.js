$(document).ready(function(){
  //Now go bind AJAX-powered event handlers for our forms
  var frm1 = $('#q1_form');
  var frm2 = $('#q2_form');
  //var frm3 = $('#q3_form');
  //var frm4 = $('#q4_form');
  //frm1
  frm1.submit(function(ev){
    $.ajax({
        type: frm1.attr('method'),
        url: frm1.attr('action'),
        data: frm1.serialize(),
        success: function (d) {
          var resultArray = $.parseJSON(d);
          resultArray.unshift(chart1DataHeader);
          chart1Data = google.visualization.arrayToDataTable(resultArray);
          drawChart1();
        }
    });
    ev.preventDefault();
  }); //frm1
  //frm2
  frm2.submit(function(ev){
    $.ajax({
        type: frm2.attr('method'),
        url: frm2.attr('action'),
        data: frm2.serialize(),
        success: function (d) {
          var resultArray = $.parseJSON(d);
          resultArray.unshift(chart2DataHeader);
          chart2Data = google.visualization.arrayToDataTable(resultArray);
          drawChart2();
        }
    });
    ev.preventDefault();
  }); //frm2

  //Setup for Chart1
  var chart1;
  var chart1DataHeader = ["Hashtag", "HashtagCount"];
  var chart1Data = google.visualization.arrayToDataTable([chart1DataHeader,["Loading...", 0]]);
  var chart1View;
  var chart1Options = {width:400, height:300,
                 vAxis: {},
                 hAxis: {gridlines: {count: 0}, baselineColor: 'none'},
                 legend: { position: "none" },
                 chartArea:{top:0,width:"50%",height:"50%"},
                 animation:{
                    duration: 900,
                    easing: 'out',
                  },
  };

  //Create the function that will redraw and animate Chart1
  function drawChart1(){
    chart1View = new google.visualization.DataView(chart1Data);
    chart1View.setColumns([0, 1,
                   { calc: "stringify",
                     sourceColumn: 1,
                     type: "string",
                     role: "annotation" }]);
    if(!chart1){
      chart1 = new google.visualization.BarChart(document.getElementById('visualization1'));
      alert("chart 1 created");
    }
    chart1.draw(chart1View, chart1Options);
  }
  drawChart1(); //first draw

  var chart2;
  var chart2DataHeader = ["HashTag", "NumHashtagsByUser", "{ role: 'annotation' }"];
  var chart2Data = google.visualization.arrayToDataTable([chart2DataHeader,["Loading...", 0, "Loading..."]]);
  var chart2View;
  var chart2Options = {width:400, height:300,
               vAxis: {},
               hAxis: {gridlines: {count: 0}, baselineColor: 'none'},
               legend: { position: "none" },
               chartArea:{top:0,width:"50%",height:"50%"},
               animation:{
                  duration: 900,
                  easing: 'out',
                },
  };

  //Create the function that will redraw and animate Chart1
  function drawChart2(){
    chart2View = new google.visualization.DataView(chart2Data);
    chart2View.setColumns([0, 1,
                 { calc: "stringify",
                   sourceColumn: 2,
                   type: "string",
                   role: "annotation" }
                 ]);
    if(!chart2){
      chart2 = new google.visualization.BarChart(document.getElementById('visualization2'));
      alert("chart 2 created");
    }
    chart2.draw(chart2View, chart2Options);
  }
  drawChart2();
  //Refresh the graphs periodically
  setInterval(function(){$("#q1_form").submit();}, 3000);
  setInterval(function(){$("#q2_form").submit();}, 3000);
  // setInterval(function(){
  //   chart1Data.setValue(1,1,20 * Math.random());
  //   drawChart1();
  // }, 1000);
});



// function createBarChart2(data, target) {
//   // Create and draw the visualization.
//   var view = new google.visualization.DataView(data);
//   view.setColumns([0, 1,
//                  { calc: "stringify",
//                    sourceColumn: 2,
//                    type: "string",
//                    role: "annotation" }
//                  ]);


//   var chart = new google.visualization.BarChart(document.getElementById(target));
//   chart.draw(view, options);
// }

// function drawTestVisualization(){
//   // Create and populate the data table.
//   var data = google.visualization.arrayToDataTable([
//     ["@User", "#Seattle"],
//     ["SeanAzlin2", 123],
//     ["BillG", 102],
//     ["Obama4Prez", 89],
//     ["JohnShivero", 83],
//     ["Muazify911", 65]
//   ]);

//   createBarChar1(data, 'visualization1');
//   createBarChar1(data, 'visualization2');
//   //createBarChar1(data, 'visualization3');
//   //createBarChar1(data, 'visualization4');
// }
