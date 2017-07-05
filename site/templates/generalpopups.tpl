<div id="add-user" class="cete-popup">
   <h4 class="cete-popup__title">Send contact request</h4>
   <div class="cete-popup__content">
      <p>
          Enter the tag of the person you wish to add.
      </p>
      <form action="../php/adduser.php" method="POST" id="add-user-form">
          <div class="mdl-textfield mdl-js-textfield border-light" style="text-align: left">
              <input class="mdl-textfield__input" name="usertag" maxlength="120" type="text" id="usertag" >
              <label class="mdl-textfield__label" for="usertag" style="color: rgba(212, 212, 212, 0.57);" required>@abc-efg-hij</label>
              <span id="usertag-error" class="mdl-textfield__error"></span>
          </div>
          <div class="mdl-dialog__actions">
              <input id="add-user-submit" type="submit" class="add-user mdl-button mdl-js-button mdl-button--raised mdl-button--colored mdl-js-ripple-effect" value="Add">
          </div>
      </form>
    </div>
</div>
