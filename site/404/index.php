<?php
require_once("../scripts/sidebar.php");

// 404 Page

$content = new StaticContent("<img alt='404 Image' src='../img/olddue.png'>"
                             ."<div style='width:100%; margin-bottom: 12px;'></div>"
                             ."<span class='big-p mdl-layout-title'>Just like the old bot your request could not be found!</span>");

(new StandardLayout($sidebar,$content,$title = "<h2>404</h2>"))->show();

?>
