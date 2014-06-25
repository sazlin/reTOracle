$(document).ready(function(){
  var frm = $('#q1_form');
  frm.submit(function(ev){
    $.ajax({
        type: frm.attr('method'),
        url: frm.attr('action'),
        data: frm.serialize(),
        success: function (d) {
          var hashtag = $('#q1_what').val();
          var resultArray = $.parseJSON(d);
          var header = ["@User", "#"+hashtag];
          resultArray.unshift(header);
          var data = google.visualization.arrayToDataTable(resultArray);
          drawVisualization(data, 'visualization1');
          $('#q1_what').val("");
        }
    });
    ev.preventDefault();
  });
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

  drawVisualization(data, 'visualization1');
  drawVisualization(data, 'visualization2');
  drawVisualization(data, 'visualization3');
  drawVisualization(data, 'visualization4');
}

function drawVisualization(data, target) {
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
