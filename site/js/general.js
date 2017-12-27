
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

function toggleProfileLink(active) {
    if (active) {
        $('#profile-url-box').removeClass('greyed-out');
    } else {
        $('#profile-url-box').addClass('greyed-out');
    }
}

function displayFormErrorsFromJSON(formErrors,popUpErrors = false)
{
    var form = null;
    $.each(formErrors, function(field, errorMessage) {
        if (form == null)
            form = $(field).closest("form");
        // Do not replace 'Required.' error
        var fieldElement = $("#" + field);
        if (!fieldElement.parent().hasClass('is-invalid')) {
            $("#" + field + "-error").text(errorMessage);
            fieldElement.parent().addClass('is-invalid');
            if(popUpErrors)
                fieldElement.parent().removeClass('border-light');
        }
    });
    // Remove errors that have since been fixed.
    form.each(function() {
        if (formErrors.hasOwnProperty($(this).attr('id')))
            $(this).removeClass('is-invalid');
            if(popUpErrors)
                $(this).addClass('border-light');
    });
}

function checkRequiredFields(form,popUpErrors = false){
    var foundMissing = false;
    form.each(function() {
        if ($.trim($(this).val()) == '') {
            $(this).parent().addClass('is-invalid');
            //console.log(this);
            if(popUpErrors)
                $(this).parent().removeClass('border-light');
            $(this).parent().find("[id$='error']").text('Required.');
            foundMissing = true;
        } else {
            $(this).parent().removeClass('is-invalid');
            if(popUpErrors)
                $(this).parent().addClass('border-light');
        }
    }); 
    return foundMissing;
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
    
    $(".mdl-layout").on('click', '#site-settings', function() {
        openWindow($("#profile-link"));
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
    
    toggleProfileLink($('#public-profile').prop('checked'));
    
    $(".mdl-layout").on('click', '#public-profile', (function() { toggleProfileLink($(this).prop('checked')); }));
    
    $(".mdl-layout").on('click', '#settings-submit', (function() {
       var $inputs = $('#settings-form :input');
        var values = {};
        $inputs.each(function() {
            var checked = $(this).prop('checked');
            if (checked)
                values[this.id] = checked;
        }); 
               $.ajax({
                type: 'POST',
                url: '../scripts/settings.php',
                dataType: 'json',
                data:values
                
            });
            closeWindow();
            return false;
      }));
      

      
});
