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




$(document).ready(function() {
  $('.add_entry').on('submit', function(event) {
    event.preventDefault();
    $.ajax('/add', {
      type: 'POST',
      data: $('form').serialize(),
      success: function(data) {
        $('.new').html(data);
        $('.add_entry').remove();

      }
    });
  });
});