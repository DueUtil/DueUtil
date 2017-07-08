
function setLogScrollSizes(){
    $('.content-box-inner').each(function() {
        var logHeight = $(this).height();
        $(this).find('.log-bg').height(logHeight-32);
    });
}

function setUpLogs(){
    var loneLog = $('.log-table');
    //console.log(loneLog.get(0));
    loneLog.floatThead({
        scrollContainer: function($table){
            return $table.closest('.log-bg');
        },
        useAbsolutePositioning: true
    });
}

$(document).ready(function() {

    setLogScrollSizes();

    $(window).resize(function () {
        setLogScrollSizes();
    });
  
    setUpLogs();
  
});
