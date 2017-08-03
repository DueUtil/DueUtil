<?php 
require_once("../scripts/sidebar.php");
require_once("../scripts/partners.php");
require_once("../scripts/util.php");


if (!isset($_GET["partner"]) or !valid_partner_id($_GET["partner"])) {
    error_404();
}

$partner_id = $_GET["partner"];


$partner_details = get_partner($partner_id);

if (is_null($partner_details) or partner_not_setup($partner_details)) {
    error_404();
}

$partner_page = new GenericThing("partner_page.tpl");
$name = htmlspecialchars($partner_details->name);
$partner_page->set_value('name', $name);
$partner_page->set_value('type', $partner_details->type);
$partner_page->set_value('image', htmlspecialchars($partner_details->image_url));
$partner_page->set_value('customlink', htmlspecialchars($partner_details->custom_link));
$partner_page->set_value('linkname', htmlspecialchars($partner_details->link_name));
$partner_page->set_value('pagecontent', $partner_details->page_content);


(new StandardLayout($sidebar,$partner_page, $title = "", "DueUtil partnered $partner_details->type - $name"))->show();

?>
