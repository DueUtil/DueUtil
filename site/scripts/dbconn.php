<?php
require_once("util.php");


# Auth
$user = "admin";
$host = "localhost";
$pwd = "DueUtil4LyfeTest999AppleAndCheese";
$manager = new MongoDB\Driver\Manager("mongodb://$user:$pwd@$host/admin?authMechanism=SCRAM-SHA-1");
// $db = $client->selectDB("dueutil");

function get_collection_data($collection) {
    global $manager;
    
    // This is for collections made for this site that only have a single block a data
    $find_all_query = new MongoDB\Driver\Query(array());
    $cursor = $manager->executeQuery("dueutil.$collection",$find_all_query);
    $data = object_to_array($cursor->toArray()[0]);
    return $data;
}
?>
