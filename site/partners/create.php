<?php

require_once("../scripts/needsauth.php");
require_once("../scripts/constants.php");

if (strcmp($user_data["id"], OWNER) === 0) {
  $partner = array ('name'=>"Test"
                    'image_url'=>"",
                    'description'=>"",
                    'custom_link'=>"",
                    'link_name'=>"",
                    'page_content'=>"");
  
} else {
    echo "Unauthorized";
    http_response_code(401);
    die();
}
?>
