<!doctype html>
<!--
OH SHITTTT!

You just did view source on my page!
That means your now a certified hacker man and have totally hacked me.
-->
<html lang="en">
   <head>
      <meta charset="utf-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width, initial-scale=0.9, minimum-scale=0.9">
      <title>DueUtil - [@pagename]</title>
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
      [@header]
      <script src="../js/material.min.js"></script>
      <link rel="icon" type="image/png" href="../img/logo.png" />
      <link rel="stylesheet" type="text/css" href="../css/due-style.css">
      <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:regular,bold,italic,thin,light,bolditalic,black,medium&amp;lang=en">
      <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
      <link rel="stylesheet" href="../css/material.min.css" />
      <link rel="stylesheet" href="../css/dueutil-icons.css" />
      <!-- <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js"></script>
      <script type='text/javascript' src="https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.10/jquery.mask.min.js"></script>
      <script type='text/javascript' src="https://cdn.rawgit.com/SamWM/jQuery-Plugins/master/numeric/jquery.numeric.min.js"></script>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/1.6.0/clipboard.min.js"></script> 
      <link rel="stylesheet" href="https://cdn.rawgit.com/CreativeIT/getmdl-select/master/getmdl-select.min.css">
      <script defer src="https://cdn.rawgit.com/CreativeIT/getmdl-select/master/getmdl-select.min.js"></script> -->
      <script src="https://cdnjs.cloudflare.com/ajax/libs/floatthead/2.0.3/jquery.floatThead.min.js"></script>
      <!-- Meta -->
      <meta name="author" content="MacDue">
      <meta name="description" content="[@pagedesc]" property="og:description">
      <!-- Open graph meta -->
      <meta property="og:url" content="http://dueutil.tech/">
      <meta property="og:type" content="website">
      <meta property="og:title" content="DueUtil - [@pagename]">
      <meta content="DueUtil" property="og:site_name">
      <meta property="og:image" content="http://dueutil.tech/img/logo.png">
      <meta content='image/png' property='og:image:type'>
   </head>
   <body>
      <div id="overlay"></div>
      <div id="alert-snackbar" class="mdl-js-snackbar mdl-snackbar">
          <div class="mdl-snackbar__text"></div>
          <button class="mdl-snackbar__action" type="button"></button>
      </div>
      <div class="mdl-layout mdl-js-layout mdl-layout--fixed-drawer mdl-layout--fixed-header">
         [@body]
         <header class="mdl-layout__header">
            <div id="page-header" class="mdl-layout__header-row">
               <a href="../home/" style="height:100%">
                 <img src="../img/logo.png" class="cete-logo" alt="DueUtil logo">
               </a>
               <!-- Title -->
               <span class="mdl-layout-title"><span>DueUtil</span></span>
               <div class="cete-header-content">
                  <div class="centre-vert-content"><span class="mdl-layout-title">[@pagename]</span></div>
               </div>
               <div id="cete-header-buttons">
                  [@headerbuttons]
                  <button id="options-button"
                     class="mdl-button mdl-js-button mdl-button--icon">
                  <i class="material-icons">more_vert</i>
                  </button>
                  <ul style="width:auto" class="mdl-menu mdl-menu--bottom-right mdl-js-menu mdl-js-ripple-effect"
                     for="options-button">
                     [@dropdownoption]
                  </ul>
               </div>
            </div>
         </header>
         [@sidebar]
         <main style="position: relative" class="mdl-layout__content">
            <span id="content-title" class="mdl-layout-title">[@contenttitle]</span>
            <div class="[@flexstyle]">
               [@content]
               <div style="width:100%"></div>
               <div style="flex-grow: 1;"></div>
               <footer id="due-footer" class="mdl-mini-footer">
                <div class="mdl-mini-footer__left-section">
                  <div class="mdl-logo">DueUtil &copy; 2017 MacDue&#x23;4453 (Ben) - <a class="due-link" href="mailto:macdue@dueutil.tech" target="_top">Contact</a></div>
                </div>
              </footer>   
            </div>
         </main>
      
      </div>
   </body>
</html>
