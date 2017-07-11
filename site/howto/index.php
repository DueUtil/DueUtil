<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/util.php");


$admin_help = due_markdown_to_html(file_get_contents('./admin.txt'));
$player_help = due_markdown_to_html(file_get_contents('./player.txt'));

$content = array();
$content[] = new StaticContent('<div id="jumpers"><a class="due-link" href="#newpg">New players\' guide</a> - <a href="#adming" class="due-link">Server admins\' guide</a></div>');
$content[] = new StaticContent('<div style="width:100%"><h3 id="newpg" style="width:"><i class="material-icons">keyboard_arrow_right</i>New players\' guide</h3></div>');
$content[] = new Box($player_help);
$content[] = new StaticContent('<div style="margin-top: 12px; width:100%"><h3 id="adming"><i class="material-icons">keyboard_arrow_right</i>Server admins\' guide</h3></div>');
$content[] = new Box($admin_help);

$page = new StandardLayout($sidebar,$content, $title="<h2>How to Due</h2>");
$page->set_css('../css/discord-embeds.css');

$page->show();

?>
