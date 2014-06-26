$(document).ready(function(){
    setInterval(function(){
        $.get("/ticker", function(data) {
            alert("Query made to ticker");
            $("#twitter_tick").append( "Name: " + data );
         }, "json" );
    }, 5000)
});












// test ajax

// $(document).ready(function(){
//     window.setInterval(function(){
//         $.ajax("/ticker", function(data){
//             type: 'GET'
//             var result = $.parseJSON(data)
//             $("#tickerdiv").html(data);

//         }

//     }), } 5000);


// })







// learning journal AJAX that worked


// $(document).ready(function() {
//   $('.add_entry').on('submit', function(event) {
//     event.preventDefault();
//     $.ajax('/add', {
//       type: 'POST',
//       data: $('form').serialize(),
//       success: function(data) {
//         $('.new').html(data);
//         $('.add_entry').remove();

//       }
//     });
//   });
// });