<?php

require_once("../scripts/needsauth.php");
require_once("../scripts/constants.php");
require_once("../scripts/util.php");
require_once("../scripts/partners.php");
require_once("../scripts/discordstuff.php");



$TYPES = ["bot","server","other"];

if (strcmp($user_data["id"], OWNER) === 0) {
    if (isset($_POST["owner-id"],$_POST["project-name"],$_POST["type"])) {
      
        $owner_id = $_POST["owner-id"];
        $project_name = $_POST["project-name"];
        $type = $_POST["type"];
        
        if (!(is_numeric($_POST["owner-id"]) and is_string($project_name) 
              and is_string($type) and in_array(strtolower($type), $TYPES)
              and strlen(trim($owner_id)) > 0 and strlen(trim($project_name)) > 0)) {
            echo "Bad Request!";
            http_response_code(400);
            die();
        }
        
        $type = strtolower($type);
        
        $partner = array ('name'=> $project_name,
                          'image_url'=> null,
                          'description'=> null,
                          'custom_link'=> null,
                          'link_name'=> null,
                          'page_content'=> null,
                          'owner_id'=> $owner_id,
                          'type' => $type);
                          
        $id = strtolower(preg_replace("/[^A-Za-z0-9]/", '', $project_name));
        
        if (strlen($id) === 0) {
            echo "Invaild project name";
            http_response_code(400);
            die();
        }

        upsert('partners', $id, ['details' => $partner], $set_mode='$setOnInsert');
        
        echo "Done!";
        http_response_code(200);
        $type_emoji = partner_type_emoji((object)$partner);
        send_webhook(EDIT_WEBHOOK, array("content" => "<@$user_data[id]> has added **$project_name** $type_emoji by <@$owner_id> as partner!"));
  
    } else {
        $page = new StandardLayout($sidebar, new StaticContent("create_partner.tpl"), 
                                   $title = "<h2>Create Partner</h2>", "MacDue's private partner creation page.");
        $page->set_script("https://cdn.rawgit.com/CreativeIT/getmdl-select/master/getmdl-select.min.js");
        $page->set_css("https://cdn.rawgit.com/CreativeIT/getmdl-select/master/getmdl-select.min.css");
        $page->show();
    }
} else {
    echo "Unauthorized";
    http_response_code(401);
    die();
}
?>
