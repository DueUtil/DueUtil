<?php
require_once("../scripts/needsauth.php");
require_once("../scripts/dbconn.php");


if (!isset($_GET["partner"])) {
    error_404();
}

$partner_id = $_GET["partner"];
if (!(is_string($partner_id) 
      or strcmp(preg_replace("/[^a-z0-9 ]/", '', $partner_id), $partner_id) === 0)){
    error_404();
}


$find_object_partner_query = new MongoDB\Driver\Query(array('_id' => $partner_id));
$cursor = $manager->executeQuery("dueutil.partners", $find_object_partner_query);

$partner_data = $cursor->toArray();
if (sizeof($partner_data) == 1 && is_object($partner_data[0])) {
    $partner_data = $partner_data[0]->details;
} else {
    error_404();
}

if (!isset($_POST["name"], $_POST["image-url"], 
           $_POST["description"], $_POST["custom-link"], 
           $_POST["link-name"], $_POST["page-content"], $_POST["partner-id"])) {
             
             
    $form = new GenericThing("edit_partner.tpl");

    $form->set_value();
    
    $page = new StandardLayout($sidebar,new StaticContent("edit_partner.tpl"), $title = "<h2>Partner - Editing</h2>", "Super secret editing page!");
    $page->set_script("edit.js");
    $page->show();
} else {
    
    # Edit page data.
    
    var_dump($_POST);
  
  
}

function error_404() {
    global $sidebar;
    (new Error404Page($sidebar))->show();
    die();
}
?>
