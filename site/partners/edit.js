$(document).ready(function() {

    $(".mdl-layout").on('click', '#edit-submit', (function() {
        var form = $("#partner-details");
        checkRequiredFields($("#partner-details :input"));
        
        $.ajax({
            type: 'POST',
            url: '/partners/edit/',
            dataType: 'json',
            data: form.serialize(),
            success: function(formErrors) {

            },
            error: function() {
            }
        }); 
        
        return false;


      }));
      
});
