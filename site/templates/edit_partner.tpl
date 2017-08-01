<div class="edit-box due-command-box mdl-shadow--6dp">
  <form id="partner-details">
   <span style="margin-bottom: 12px;" class="mdl-layout-title group-title">Details</span>
       The name of your thing!<br>
    <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
     <input class="mdl-textfield__input" id="name" name="name"/>
      <label class="mdl-textfield__label" for="name">Partner name</label>
      <span id="name-error" class="mdl-textfield__error"></span>
    </div><br>
           Avatar/logo image url (for best results use a square image).<br>
    <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
     <input class="mdl-textfield__input" id="image-url" name="image-url"/>
      <label class="mdl-textfield__label" for="image-url">Image url</label>
      <span id="image-url-error" class="mdl-textfield__error"></span>
    </div><br>
    Short description of your thing (400 words max).<br>
      <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
    <textarea class="mdl-textfield__input" maxlength="400" type="text" rows= "3" id="description" name="description"></textarea>
    <label class="mdl-textfield__label" for="description">Partner description...</label>
    <span id="description-error" class="mdl-textfield__error">gff</span>
  </div>
  <br>
   A link to whatever you want (for your partner card).<br>
    <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
     <input class="mdl-textfield__input" id="custom-link" name="custom-link"/>
      <label class="mdl-textfield__label" for="custom-link">Custom link</label>
        <span id="custom-link-error" class="mdl-textfield__error"></span>
    </div><br>
     A short one or two word name for your custom link.<br>
    <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
     <input class="mdl-textfield__input" id="link-name" name="link-name"/>
      <label class="mdl-textfield__label" for="link-name">Custom link name</label>
          <span id="link-name-error" class="mdl-textfield__error"></span>
    </div><br>
   <span style="margin-bottom: 12px;" class="mdl-layout-title group-title">Page</span>
   Edit your partner page. You can use custom css and html here but no javascript!<br>
  <div style="margin-top: -12px;" class="mdl-textfield mdl-js-textfield">
    <textarea class="mdl-textfield__input" maxlength="400" type="text" rows= "3" id="page-content" name="page-content"></textarea>
    <label class="mdl-textfield__label" for="page-content">Page contents...</label>
      <span id="page-content-error" class="mdl-textfield__error"></span>
  </div><br>
    <input type="hidden" name="partner-id" value="[@id]">
  <button id="edit-submit" class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" data-upgraded=",MaterialButton">
    Submit edit
   </button>
  </form>
</div>
