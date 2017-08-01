<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/dbconn.php");


(new StandardLayout($sidebar,new StaticContent("edit_partner.tpl"), $title = "<h2>Partner - Editing</h2>", "Super secret editing page!"))->show();
?>
