<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/util.php");


$admin_help = file_get_contents('./admin.txt');

$admin_help = due_markdown_to_html($admin_help);

$content = array();
$content[] = new Box($admin_help);

$page = new StandardLayout($sidebar,$content, $title="<h2>How to</h2>");
$page->set_css('../css/discord-embeds.css');

$page->show();

?>
