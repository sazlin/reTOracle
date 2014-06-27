$(document).ready(function(){
    setInterval(function(){
        $.get("/ticker", '', function(data) {
            var val1 = data[0][0];
            var val2 = data[0][1];
            $(".twitter_tick").replaceWith("<p>" + val1 + ": " + val2 + "</p>");
         }, "json" );
    }, 3000)
});

