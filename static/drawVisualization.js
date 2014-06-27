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
  var chart1Options = {width:400, height:200,
                 vAxis: {},
                 hAxis: {gridlines: {count: 0}, baselineColor: 'none'},
                 legend: { position: "none" },
                 chartArea:{width:"65%",height:"100%"},
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
    }
    chart1.draw(chart1View, chart1Options);
  }
  drawChart1(); //first draw

  var chart2;
  var chart2DataHeader = ["HashTag", "NumHashtagsByUser", "{ role: 'annotation' }"];
  var chart2Data = google.visualization.arrayToDataTable([chart2DataHeader,["Loading...", 0, "Loading..."]]);
  var chart2View;
  var chart2Options = {width:400, height:200,
               vAxis: {},
               hAxis: {gridlines: {count: 0}, baselineColor: 'none'},
               legend: { position: "none" },
               chartArea:{width:"65%",height:"100%"},
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
  // add all your code to this method, as this will ensure that page is loaded
  //AmCharts.ready(function() {
  //Twitter icon :)
  var icon = "M26.492,9.493c-0.771,0.343-1.602,0.574-2.473,0.678c0.89-0.533,1.562-1.376,1.893-2.382c-0.832,0.493-1.753,0.852-2.734,1.044c-0.785-0.837-1.902-1.359-3.142-1.359c-2.377,0-4.306,1.928-4.306,4.306c0,0.337,0.039,0.666,0.112,0.979c-3.578-0.18-6.75-1.894-8.874-4.499c-0.371,0.636-0.583,1.375-0.583,2.165c0,1.494,0.76,2.812,1.915,3.583c-0.706-0.022-1.37-0.216-1.95-0.538c0,0.018,0,0.036,0,0.053c0,2.086,1.484,3.829,3.454,4.222c-0.361,0.099-0.741,0.147-1.134,0.147c-0.278,0-0.547-0.023-0.81-0.076c0.548,1.711,2.138,2.955,4.022,2.99c-1.474,1.146-3.33,1.842-5.347,1.842c-0.348,0-0.69-0.021-1.027-0.062c1.905,1.225,4.168,1.938,6.6,1.938c7.919,0,12.248-6.562,12.248-12.25c0-0.187-0.002-0.372-0.01-0.557C25.186,11.115,25.915,10.356,26.492,9.493";
  // create AmMap object
  var map = new AmCharts.AmMap();
  // set path to images
  map.pathToImages = "static/ammap/images/";

  /* create data provider object
   map property is usually the same as the name of the map file.

   getAreasFromMap indicates that amMap should read all the areas available
   in the map data and treat them as they are included in your data provider.
   in case you don't set it to true, all the areas except listed in data
   provider will be treated as unlisted.
  */
  // var dataProvider = {
  //   map: "worldLow",
  //   images:[{latitude:40.3951, longitude:-73.5619, svgPath:icon, color:"#00F", scale:0.5, label:"New York", labelShiftY:2}]
  // };

  var dataProvider = {"map": "worldLow",images:[{latitude:42.1457681573,longitude:-3.13560974398,svgPath:icon, color:"#00F",scale:0.5,labelShiftY:2,zoomLevel:5,title:"cicsolutions",label:"cicsolutions",description:"Hi everyone on #LancashireHour #lancashireh were a PHP Web Development agency based in Chorley. http://t.co/zSg2Y947qN #php #codeigniter"}]};
  // pass data provider to the map object
  map.dataProvider = dataProvider;

  /* create areas settings
   * autoZoom set to true means that the map will zoom-in when clicked on the area
   * selectedColor indicates color of the clicked area.
   */
  map.areasSettings = {
      autoZoom: true,
      selectedColor: "#00F"
  };

  // let's say we want a small map to be displayed, so let's create it
  map.smallMap = new AmCharts.SmallMap();

  // write the map to container div
  map.write("mapdiv");

  function setMapData(data){
    //alert(data);
    map.clearLabels();
    //var newDataProvider = {"map": "worldLow",images:[{latitude:32.1457681573,longitude:-13.13560974398,svgPath:icon, color:"#00F",scale:0.5,zoomLevel:5,title:"NEW",label:"NEW",description:"Hi everyone on #LancashireHour #lancashireh were a PHP Web Development agency based in Chorley. http://t.co/zSg2Y947qN #php #codeigniter"}]};
    //map.dataProvider = newDataProvider;
    map.dataProvider = data;
    map.validateNow();
  }

  setInterval(function(){
    $.get( "/geotweet", function( data ) {
      // alert("geotweet response: " + data);
      if(data != "unchanged"){
          setMapData(data);
      }
    });
  }, 3000);
});

