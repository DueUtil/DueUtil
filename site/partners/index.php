<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/dbconn.php");

$find_all_partners_query = new MongoDB\Driver\Query(array());
$cursor = $manager->executeQuery("dueutil.partners",$find_all_partners_query);
$partners = $cursor->toArray();

$partner_cards = array();

foreach($partners as $partner) {
    $id = $partner->_id;
    $details = $partner->details;
    
    foreach($details as $detail) {
        if (is_null($detail))
            continue 2;
    }

    $partner_cards[] = new PartnerCard($name=$details->name, $type=$details->type, 
                                       $image=$details->image_url, $message=$details->description,
                                       $page=$id, $link_name=$details->link_name, $link=$details->custom_link);
}

if (sizeof($partner_cards) === 0) {
    $partner_cards[] = new StaticContent("<h4>No partners... How sad ;(</h4>");
}

$page = new StandardLayout($sidebar,$partner_cards, $title = "<h2>Partners</h2>", "DueUtil partnered discord bots, servers, and other things!");
$page->set_value('flexstyle', "command-list");
$page->show();
?>
