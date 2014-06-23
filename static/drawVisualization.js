function drawTestVisualization(){
  // Create and populate the data table.
  var data = google.visualization.arrayToDataTable([
    ['@User', '#Seattle'],
    ['SeanAzlin2', 123],
    ['BillG', 102],
    ['Obama4Prez', 89],
    ['JohnShivero', 83],
    ['Muazify911', 65]
  ]);
  drawVisualization(data, 'visualization1');
  drawVisualization(data, 'visualization2');
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
                 legend: { position: "none" }
                };

  var chart = new google.visualization.BarChart(document.getElementById(target));
  chart.draw(view, options);



}