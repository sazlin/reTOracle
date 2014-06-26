window.setInterval(function() {
    $.get("/ticker", function(data) {
        $("#tickerdiv").html(data); }); }, 5000);




$(document).ready(function(){
    window.setInterval(function(){
        $.get("/ticker", function(data){
            var result = $.parseJSON(data)
            $("#tickerdiv").html(data);

        }

    }), } 5000);


})