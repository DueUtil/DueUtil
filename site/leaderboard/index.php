<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/dbconn.php");
require_once("../scripts/players.php");

/*
 * Leaderboard
 */
 
$page = new StandardLayout($sidebar,new Leaderboard(),$title = "<h2>Global Leaderboard</h2>");

$page->set_css('../css/due-style-tables.css');
$page->show();

?>
