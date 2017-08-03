<script type="text/javascript">
    $(document).ready(function() {
        $(".mdl-layout").on('click', '#partner-submit', (function() {
            var form = $("#create-partner");
            console.log(checkRequiredFields($("#create-partner :input")));
            if(!checkRequiredFields($("#create-partner :input"))) {
                console.log('dds');
                $.ajax({
                    type: 'POST',
                    url: '/partners/create.php',
                    data: form.serialize(),
                    success: function() {
                        window.location = "/partners/edit/"+$("#project-name").val().replace(/[^0-9a-zA-Z]/g, "").toLowerCase();
                    },
                    error: function(xhr, status, error) {
                        alert("Could not create partner: "+xhr.responseText);
                    }
                }); 
            }
            return false;
          }));
    });
</script>
<div style="overflow: visible;" class="edit-box due-command-box mdl-shadow--6dp">
  <form id="create-partner">
   <span style="margin-bottom: 12px;" class="mdl-layout-title group-title">Partner Creation</span>
       Owner Discord ID<br>
    <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
     <input class="mdl-textfield__input" id="owner-id" name="owner-id"/>
      <label class="mdl-textfield__label" for="name">Owner ID</label>
      <span id="owner-id-error" class="mdl-textfield__error"></span>
    </div><br>
       Partner project name!<br>
    <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
     <input class="mdl-textfield__input" id="project-name" name="project-name"/>
      <label class="mdl-textfield__label" for="name">Partner name</label>
      <span id="project-name-error" class="mdl-textfield__error"></span>
    </div><br>
           Partner project type (bot/server/other).<br>
   <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label getmdl-select">
     <input class="mdl-textfield__input" id="type" name="type" value="Bot" type="text" readonly tabIndex="-1" data-val="Bot"/>
       <label class="mdl-textfield__label" for="type">Type</label>
       <ul class="mdl-menu mdl-menu--bottom-left mdl-js-menu" for="type">
         <li class="mdl-menu__item" data-val="Bot">Bot</li>
         <li class="mdl-menu__item" data-val="Server">Server</li>
         <li class="mdl-menu__item" data-val="Other">Other</li>
       </ul>
   </div><br>
  <button value="Create" id="partner-submit" class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" data-upgraded=",MaterialButton">
    Create partner
   </button>
  </form>
</div>
