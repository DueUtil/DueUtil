<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/dbconn.php");

if (!isset($_POST["name"], $_POST["image-url"], 
           $_POST["description"], $_POST["custom-link"], 
           $_POST["link-name"], $_POST["page-content"], $_POST["partner-id"])) {
             
    # Edit page form
    $page = new StandardLayout($sidebar,new StaticContent("edit_partner.tpl"), $title = "<h2>Partner - Editing</h2>", "Super secret editing page!");
    $page->set_script("edit.js");
    $page->show();
} else {
    
    # Edit page data.
    
    var_dump($_POST);
  
  
}
?>
