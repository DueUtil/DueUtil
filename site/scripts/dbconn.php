<?php
# Auth
$user = "admin";
$host = "localhost";
$pwd = "DueUtil4LyfeTest999AppleAndCheese";
$manager = new MongoDB\Driver\Manager("mongodb://$user:$pwd@$host/admin?authMechanism=SCRAM-SHA-1");
// $db = $client->selectDB("dueutil");
?>
