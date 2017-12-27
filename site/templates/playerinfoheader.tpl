<div class="player-stats-dash" >[@attack]<span class="player-icon-inline icon-fist-profile"></span>[@strg]<span class="player-icon-inline icon-strg"></span>[@accy]<span class="player-icon-inline icon-accy"></span></div>
<div style="width:100%"></div>
<div id="exp-message">[@expneeded] EXP for <span class="level">Level [@nextlevel]</span></div>
<div style="width:100%"></div>
<div id="player-exp" class="mdl-progress mdl-js-progress"></div>
<script>
  document.querySelector('#player-exp').addEventListener('mdl-componentupgraded', function() {
    this.MaterialProgress.setProgress([@progress]);
  });
</script>
<div style="width:100%"></div>
