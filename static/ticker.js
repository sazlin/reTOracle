$(document).ready(function(){
    setInterval(function(){
        $.get("/ticker", '', function(data) {
            var val1 = data[0][0];
            var val2 = data[0][1];
            $(".alert-info p").replaceWith("<p><b>" + val1 + "</b>" + ": " + val2 + "</p>");
            //$(".twitter_tick p").css("background-color: #66CCFF");
         }, "json" );
    }, 3000)
});


