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
          //var hashtag = $('#q1_what').val();
          var resultArray = $.parseJSON(d);
          var header = ["Hashtag", "HashtagCount"];
          resultArray.unshift(header);
          var data = google.visualization.arrayToDataTable(resultArray);
          drawBarChart1(data, 'visualization1');
          //$('#q1_what').val("");
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
          var header = ["HashTag", "NumHashtagsByUser", "{ role: 'annotation' }",];
          resultArray.unshift(header);
          var data = google.visualization.arrayToDataTable(resultArray);
          drawBarChart2(data, 'visualization2');
        }
    });
    ev.preventDefault();
  }); //frm2

  //Refresh the forms periodically
  setInterval(function(){$("#q1_form").submit();}, 3000);
  setInterval(function(){$("#q2_form").submit();}, 3000);
  //frm3
//   frm3.submit(function(ev){
//     $.ajax({
//         type: frm3.attr('method'),
//         url: frm3.attr('action'),
//         data: frm3.serialize(),
//         success: function (d) {
//           var mention = $('#q3_who').val();
//           var resultArray = $.parseJSON(d);
//           var header = ["@User", "@"+mention];
//           resultArray.unshift(header);
//           var data = google.visualization.arrayToDataTable(resultArray);
//           drawBarChart1(data, 'visualization3');
//           $('#q3_who').val("");
//         }
//     });
//     ev.preventDefault();
//   }); //frm3
//   //frm4
//   frm4.submit(function(ev){
//     $.ajax({
//         type: frm4.attr('method'),
//         url: frm4.attr('action'),
//         data: frm4.serialize(),
//         success: function (d) {
//           var mention = $('#q4_who').val();
//           var resultArray = $.parseJSON(d);
//           var header = ["@User", "@"+mention];
//           resultArray.unshift(header);
//           var data = google.visualization.arrayToDataTable(resultArray);
//           drawBarChart1(data, 'visualization4');
//           $('#q4_who').val("");
//         }
//     });
//     ev.preventDefault();
//   }); //frm4
});

function drawTestVisualization(){
  // Create and populate the data table.
  var data = google.visualization.arrayToDataTable([
    ["@User", "#Seattle"],
    ["SeanAzlin2", 123],
    ["BillG", 102],
    ["Obama4Prez", 89],
    ["JohnShivero", 83],
    ["Muazify911", 65]
  ]);

  drawBarChart1(data, 'visualization1');
  drawBarChart1(data, 'visualization2');
  //drawBarChart1(data, 'visualization3');
  //drawBarChart1(data, 'visualization4');
}

function drawBarChart1(data, target) {
  // Create and draw the visualization.
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1,
                   { calc: "stringify",
                     sourceColumn: 1,
                     type: "string",
                     role: "annotation" }]);
  var options = {width:400, height:300,
                 vAxis: {},
                 hAxis: {gridlines: {count: 0}, baselineColor: 'none'},
                 legend: { position: "none" },
                 chartArea:{top:0,width:"50%",height:"50%"}
                };

  var chart = new google.visualization.BarChart(document.getElementById(target));
  chart.draw(view, options);
}

function drawBarChart2(data, target) {
  // Create and draw the visualization.
  var view = new google.visualization.DataView(data);
  view.setColumns([0, 1,
                 { calc: "stringify",
                   sourceColumn: 2,
                   type: "string",
                   role: "annotation" }
                 ]);
  var options = {width:400, height:300,
                 vAxis: {},
                 hAxis: {gridlines: {count: 0}, baselineColor: 'none'},
                 legend: { position: "none" },
                 chartArea:{top:0,width:"50%",height:"50%"}
                };

  var chart = new google.visualization.BarChart(document.getElementById(target));
  chart.draw(view, options);
}
