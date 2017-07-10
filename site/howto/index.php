<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/util.php");


$admin_help = due_markdown_to_html(file_get_contents('./admin.txt'));
$player_help = due_markdown_to_html(file_get_contents('./player.txt'));

$content = array();
$content[] = new Box($player_help);
$content[] = new Box($admin_help);

$page = new StandardLayout($sidebar,$content, $title="<h2>How to Due</h2>");
$page->set_css('../css/discord-embeds.css');

$page->show();

?>
