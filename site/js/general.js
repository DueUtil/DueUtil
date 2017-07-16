
var windowOriginalStates = new Array();
var openWindowElement = null;
var windowOpening = false;


$(document).ajaxSend(function( event, jqxhr, settings ) {
    jqxhr.setRequestHeader("Cete-Ajax-Request", window.location.href)
});


/*
 * Helper method to open a window passed as a Jquery object
 * Set restoreStateOnClose to true if you want the window to reset to 
 * how it was one page load for the next time it is opened.
 */
function openWindow(window, noOverlay = false) {
    if (openWindowElement != null)
        closeWindow();
    windowOpening = true;
    setTimeout(function(){windowOpening = false;},200);
    if (!noOverlay)
        $("#overlay").fadeIn(200);
    window.show();
    openWindowElement = window;
}

/*
 * Helper method to close the currenly open window
 */
function closeWindow() {
    if (openWindowElement == null)
        return;
    var position = $(".mdl-layout__content").scrollTop();
    var windowId = openWindowElement.attr('id');
    if (typeof windowOriginalStates[windowId] !== 'undefined') {
        $('#' + windowId).replaceWith(upgradeMDL(windowOriginalStates[windowId]));
    }
    $("#overlay").fadeOut(200);
    openWindowElement.hide();
    openWindowElement = null;
    $(".mdl-layout__content").scrollTop(position);
    dispatchWindowCloseEvent(windowId);
    
}

function dispatchWindowCloseEvent(windowId)
{
    window.dispatchEvent(new CustomEvent('windowClosed',{detail:{windowId:windowId}}));
}


/*
 * Helper method for replacing html that contains MDL objects.
 * All MDL js components need to be 'upgraded' before they are used
 * or they won't work
 */
function upgradeMDL(html) {
    if (!(html instanceof jQuery))
        html = $(html);
    html.find('*').each(function() {
        var classes = $(this).attr('class');
        if (classes !== undefined && classes.includes('mdl-')) {
            var element = $(this).get(0);
            componentHandler.upgradeElement(element);
        }
    });
    return html;
}

/*
 * Helper method to call on page load for windows that need to
 * be restored to their orignal state on close.
 */
function saveDefaultWindowState(window) {
    if (typeof windowOriginalStates[window.attr('id')] === 'undefined')
        windowOriginalStates[window.attr('id')] = window.get(0).outerHTML;
}

function sendSnackBarAlert(message,duration = 3000)
{
    var snackbar = document.querySelector('#alert-snackbar');
    snackbar.MaterialSnackbar.showSnackbar({message: message, timeout: duration});
}

$(document).ready(function() {
    $("#overlay").click(closeWindow);
    
    $(document).click(function(event) { 
        if (openWindowElement == null || windowOpening)
            return;
        windowId = '#'+openWindowElement.attr('id');
        if($('#overlay').css('display') === 'none' && event.target.id != windowId && !$(windowId).find(event.target).length) {
            closeWindow();
        }        
    });
    

    $(document).keyup(function(e) {
        if (e.keyCode == 27) closeWindow();
    });

    $('.mdl-textfield__input').on('input', function() {
        if ($(this).parent().hasClass('is-invalid')) {
            $(this).parent().removeClass('is-invalid').addClass('border-light');
        }
    });
    
    $(window).on('resize', function(){
        // Close info popup if draw closes.
        if ($('.mdl-layout').hasClass('is-small-screen') && $(openWindowElement).attr('id') === 'sidebar-info')
            closeWindow();
    });
    
    window.addEventListener('windowClosed', function (event) {
        if (event.detail.windowId === 'sidebar-info')
            if(lastSelectedMember != null){
                lastSelectedMember.css('background-color','');
            }
    });
});
