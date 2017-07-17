<div id="profile-link" class="cete-popup">
   <h4 class="cete-popup__title">Site settings</h4>
   <div class="cete-popup__content">
      <p id="settings-message" >
          A few little things to fiddle with.
      </p>
      <div id="settings">
            <form id="settings-form">
        <label class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect" for="public-profile">
          <input type="checkbox" id="public-profile" class="mdl-checkbox__input" [@checked]>
          <span class="mdl-checkbox__label">Public profile</span>
        </label>
        <div class="greyed-out" id="profile-url-box">
        Your public profile:
        <div id="profile-url">
        <a class="due-link" href="https://dueutil.tech/player/id/[@playerid]/">https://dueutil.tech/player/id/[@playerid]/</a>
        </div>
        </div>
        </form>
      </div>
      <div class="mdl-dialog__actions">
          <input id="settings-submit" type="submit" class="add-user mdl-button mdl-js-button mdl-button--raised mdl-button--colored mdl-js-ripple-effect" value="Apply">
      </div>
      </div>
</div>
