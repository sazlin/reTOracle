$(document).ready(function(){
    setInterval(function(){
        $.get("/ticker", function(data) {
            var data = $.parseJSON(data)
            $("#twitter_tick").append(data);
         }, "json" );
    }, 3000)
});

