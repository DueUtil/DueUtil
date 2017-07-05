<?php
require_once("../scripts/sidebar.php");


/*
 * The home page
 */

// Show dashboard.
(new StandardLayout($sidebar,new HomePageContent()))->show();
?>
