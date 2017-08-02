<?php
require_once("dbconn.php");

define("EDIT_WEBHOOK", "https://discordapp.com/api/webhooks/342368899259695107/0-ck4QlEHldInTuaTxdXfs9y-Of3PUHeVrWunnKb9vrFfk_DUwOSnxuKPK0NTK86RA-t");
define("PARTNER_WEBHOOK", "https://discordapp.com/api/webhooks/342006162192859157/tw2mSV-XFP7cnqziIj0omeYRM7rvI6_3v-kJmzaCUALFqLmCZZiEamJ3HwegOn7UXVFZ");


function get_partner($partner_id) {
    global $manager;
    $find_object_partner_query = new MongoDB\Driver\Query(array('_id' => $partner_id));
    $cursor = $manager->executeQuery("dueutil.partners", $find_object_partner_query);

    $partner_data = $cursor->toArray();
    if (sizeof($partner_data) == 1 && is_object($partner_data[0])) {
        return $partner_data = $partner_data[0]->details;
    } else {
        return null;
    }
}


function valid_partner_id($partner_id) {
    return is_string($partner_id) and strcmp(preg_replace("/[^a-z0-9]/", '', $partner_id), $partner_id) === 0;
}


function partner_not_setup($partner) {
    return is_null($partner->image_url);
}
?>
