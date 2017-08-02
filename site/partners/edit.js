$(document).ready(function() {

    $(".mdl-layout").on('click', '#edit-submit', (function() {
        var form = $("#partner-details");
        checkRequiredFields($("#partner-details :input"));
            $.ajax({
                type: 'POST',
                url: '/partners/edit/'+$("#partner-id").val(),
                data: form.serialize(),
                success: function() {
                    alert("DEBUG: Done!");
                },
                error: function(xhr) {
                    displayFormErrorsFromJSON(jQuery.parseJSON(xhr.responseText));
                }
            }); 
        return false;


      }));
      

    $(".mdl-layout").on('click', '#delete', (function() {
        openWindow($("#delete-cnf"));
        return false;
      }));
      
    $(".mdl-layout").on('click', '#delete-this-now', (function() {
        $.ajax({
                type: 'POST',
                url: '/partners/edit/'+$("#partner-id").val(),
                data: "delete-this=now",
                success: function() {
                    alert("Deleted!");
                }
            }); 
        return false;
      }));
      
});
