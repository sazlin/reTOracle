function drawVisualization() {
  // Create and populate the data table.
  var data = google.visualization.arrayToDataTable([
    ['@User', '#Seattle'],
    ['SeanAzlin2', 123],
    ['BillG', 102],
    ['Obama4Prez', 89],
    ['JohnShivero', 83],
    ['Muazify911', 65]
  ]);

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
                 legend: { position: "none" }
                };
  var chart_top_left = new google.visualization.BarChart(document.getElementById('visualization1'));
  var chart_top_right = new google.visualization.BarChart(document.getElementById('visualization2'));


  chart_top_right.draw(view, options);
  chart_top_left.draw(view,options);
}