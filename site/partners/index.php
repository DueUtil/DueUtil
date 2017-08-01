<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/dbconn.php");

(new StandardLayout($sidebar,new StaticContent("partner.tpl"), $title = "<h2>Partners</h2>", "DueUtil partnered discord bots, server, and other things!"))->show();

?>
