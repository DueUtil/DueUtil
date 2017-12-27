<?php
require_once("../scripts/sidebar.php");

// 404 Page

(new Error404Page($sidebar))->show();

?>
