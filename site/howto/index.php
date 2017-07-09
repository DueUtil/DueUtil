<?php
require_once("../scripts/sidebar.php");


$page = new StandardLayout($sidebar,new StaticContent('weaponembed.tpl'), $title="<h2>How to</h2>");
$page->set_css('../css/discord-embeds.css');

$page->show();

?>
