<?php
require_once("../scripts/needsauth.php");
require_once("../scripts/util.php");
require_once("../scripts/partners.php");
require_once("../scripts/discordstuff.php");


if (!isset($_GET["partner"])) {
    error_404();
}

$partner_id = $_GET["partner"];
if (!valid_partner_id($partner_id )){
    error_404();
}

$partner_data = get_partner($partner_id);
if (is_null($partner_data)) {
    error_404();
}

if (!in_array($user_data["id"], [OWNER,$partner_data->owner_id])) {
    error_404();
}

$type_emoji = partner_type_emoji($partner_data);

if (!isset($_POST["name"], $_POST["image-url"], 
           $_POST["description"], $_POST["custom-link"], 
           $_POST["link-name"], $_POST["page-content"])) {
             
    if (!isset($_POST["delete-this"])) {
        $form = new GenericThing("edit_partner.tpl");

        $form->set_value('name', $partner_data->name);
        $form->set_value('imageurl', $partner_data->image_url);
        $form->set_value('description', strip($partner_data->description));
        $form->set_value('customlink', $partner_data->custom_link);
        $form->set_value('linkname', $partner_data->link_name);
        $form->set_value('pagecontent', strip($partner_data->page_content));
        $form->set_value('id', $partner_id);

        $page = new StandardLayout($sidebar,$form, $title = "<h2>Partner - Editing</h2>", "Super secret editing page!");
        $page->body_append(new StaticContent("delete_partner.tpl"));
        $page->set_script("edit.js");
        $page->show();
    
    } else {
        echo "Okay, :( but not because you told me to.";
        $name = $partner_data->name;
        send_webhook(EDIT_WEBHOOK, array("content" => "<@$user_data[id]> deleted **$name** $type_emoji ($partner_id) :cry:"));
        delete_document($partner_id, 'partners');
    }
    
} else {
    
    $form_errors = array();
    
    $name = $_POST["name"];
    $image_url = $_POST["image-url"];
    $description = $_POST["description"];
    $custom_link = $_POST["custom-link"];
    $link_name = $_POST["link-name"];
    $page_content = $_POST["page-content"];
    
        
    if (validate_string("name", $name, 1, 32) 
            & validate_url("image-url", $image_url, $image=True)
            & validate_string("description", $description, 100, 400)
            & validate_url("custom-link", $custom_link)
            & validate_string("link-name", $link_name, 1, 32)
            & validate_html_safe("page-content", $page_content)) {
              
              
        $partner = array ('name'=> $name,
                          'image_url'=> $image_url,
                          'description'=> $description,
                          'custom_link'=> $custom_link,
                          'link_name'=> $link_name,
                          'page_content'=> $page_content,
                          'owner_id'=> $partner_data->owner_id,
                          'type' => $partner_data->type);
                          
        upsert('partners', $partner_id, ['details' => $partner]);
        
        echo "Done!";
        http_response_code(200);
        
        send_webhook(EDIT_WEBHOOK, array("content" => "<@$user_data[id]> edited partner details for **$name** $type_emoji\n"
                                                      ."<https://dueutil.tech/partners/$partner_id>"));
                                                      
        var_dump($partner_data);
                                                      
        if (partner_not_setup($partner_data)) {
            send_webhook(PARTNER_WEBHOOK, array("embeds" => [new_partner_embed($partner_id,(object)$partner)]));
        }
        
    } else {
        http_response_code(400);
        header('Content-Type: application/json');
        echo json_encode($form_errors);
        die();
    }
}


function new_partner_embed($id, $partner){
    global $user_data, $type_emoji;
    
    $embed = new Embed($title=":new: New partner!", $color=9819069);
    $embed->url = "http://localhost/partners/$id";
    $embed->set_thumbnail($url=$partner->image_url);
    $embed->add_field($name=$partner->name.' '.$type_emoji, $value=$partner->description);
    $embed->add_field($name="Partner page", $value='<'.$embed->url.'>', $inline=True);
    $embed->add_field($name=$partner->link_name, $value=$partner->custom_link, $inline=True);
    $embed->set_footer($text="This post is from $user_data[username].");
    return $embed;
}


function validate_string($var_name, $string, $min_len, $max_len) {
    global $form_errors;
    $invalid = False;
    if ($invalid = !is_string($string)) {
        $form_errors[$var_name] = "Not a string?!";
    } else if ($invalid = strlen($string) < $min_len) {
        $form_errors[$var_name] = "Length must be at least $min_len characters!";
    } else if ($invalid = strlen($string) > $max_len) { 
        $form_errors[$var_name] = "Length cannot be greater than $max_len characters!";
    }
    return !$invalid;
}


function validate_url($var_name, $url, $image=False) {
    global $form_errors;
    $invalid = False;
    if ($invalid = !is_string($url)) {
        $form_errors[$var_name] = "Not a string?!";
    } else if ($invalid = strlen($url) > 500) { 
        $form_errors[$var_name] = "URL way too long!";
    } else if ($invalid = filter_var($url, FILTER_VALIDATE_URL) === false) {
        $form_errors[$var_name] = "Not a valid URL?!";
    } else if($invalid = ($image && !is_valid_image_url($url))) {
        $form_errors[$var_name] = "URL does not point to an image!";
    }
    return !$invalid;
}


function validate_html_safe($var_name, $html, $no_scripts=True) {
    global $form_errors;
    if ($invalid = !is_string($html)) {
        $form_errors[$var_name] = "Something is strange here...";
    } else if ($invalid = strlen($html) > 20000) {
        $form_errors[$var_name] = "Too long! If you need more contact MacDue!";
    } else if ($invalid = preg_match("/(%3C*|<)[^*]?script/i", $html)) {
        $form_errors[$var_name] = "No scripts please... I don't trust you!";
    }
    return !$invalid;
}
?>
