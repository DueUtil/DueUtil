<div class="edit-box due-command-box mdl-shadow--6dp">
  <form id="partner-details">
   <span style="margin-bottom: 12px;" class="mdl-layout-title group-title">Details</span>
       The name of your thing!<br>
    <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
     <input class="mdl-textfield__input" id="name" name="name" value="[@name]"/>
      <label class="mdl-textfield__label" for="name">Partner name</label>
      <span id="name-error" class="mdl-textfield__error"></span>
    </div><br>
           Avatar/logo image url (for best results use a square image).<br>
    <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
     <input class="mdl-textfield__input" id="image-url" name="image-url" value="[@imageurl]"/>
      <label class="mdl-textfield__label" for="image-url">Image url</label>
      <span id="image-url-error" class="mdl-textfield__error"></span>
    </div><br>
    Short description of your thing (100-400 characters).<br>
      <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
    <textarea class="mdl-textfield__input" maxlength="400" type="text" rows= "3" id="description" name="description">[@description]</textarea>
    <label class="mdl-textfield__label" for="description">Partner description...</label>
    <span id="description-error" class="mdl-textfield__error">gff</span>
  </div>
  <br>
   A link to whatever you want (for your partner card).<br>
    <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
     <input class="mdl-textfield__input" id="custom-link" name="custom-link" value="[@customlink]"/>
      <label class="mdl-textfield__label" for="custom-link">Custom link</label>
        <span id="custom-link-error" class="mdl-textfield__error"></span>
    </div><br>
     A short one or two word name for your custom link.<br>
    <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
     <input class="mdl-textfield__input" id="link-name" name="link-name" value="[@linkname]"/>
      <label class="mdl-textfield__label" for="link-name">Custom link name</label>
          <span id="link-name-error" class="mdl-textfield__error"></span>
    </div><br>
   <span style="margin-bottom: 12px;" class="mdl-layout-title group-title">Page</span>
   Edit your partner page. You can use custom css and html here but no javascript!<br>
  <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
    <textarea class="mdl-textfield__input" type="text" rows= "3" id="page-content" name="page-content">[@pagecontent]</textarea>
    <label class="mdl-textfield__label" for="page-content">Page contents...</label>
      <span id="page-content-error" class="mdl-textfield__error"></span>
  </div><br>
    <input type="hidden" id="partner-id" name="partner-id" value="[@id]">
    <div>
  <button id="edit-submit" value="edit" class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" data-upgraded=",MaterialButton">
    Submit edit
   </button>
    <button  style="color:rgba(249,241,223,.87); background:#ff6961;float:right" id="delete" value="delete" class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" data-upgraded=",MaterialButton">
    Delete
   </button>
   </div>
  </form>
</div>
