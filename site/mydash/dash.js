$(window).resize(function() {
   wrapped();
});

$(document).ready(function() {
  wrapped();
  saveDefaultWindowState($("#profile-link"));
  
  $(".mdl-layout").on('click', '#add-user-btn', function() {
      openWindow($("#profile-link"));
  });
});

function wrapped() {
    var offset_top_prev;
    var height_prev;
    var count = 0;
    $('.flex-content').each(function() {
       var offset_top = $(this).offset().top;
      if (count % 2 == 1 && offset_top >= offset_top_prev+height_prev) {
         $(this).addClass('wrapped');
      } else {
         $(this).removeClass('wrapped');
      }
      offset_top_prev = offset_top;
      height_prev = $(this).height();
      count+= 1;
   });
}
