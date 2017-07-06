<?php
require_once("../scripts/dbconn.php");

function find_player($player_id)
{
    global $manager;
    $find_player_query = new MongoDB\Driver\Query(array('_id' => $player_id));
    $cursor = $manager->executeQuery('dueutil.Player',$find_player_query );
    $data = "data";
    try{
        $player_data = $cursor->toArray()[0]->$data;
        $player = json_decode($player_data, True)["py/state"];
        return $player;
    } catch (Exception $e) {
        return null;
    }
}

// Small helpers to clean up python pickles
function get_player_quests($player){
    $quests = array();
    foreach ($player["quests"] as $quest_data)
        $quests[] = $quest_data["py/state"];
    return $quests;
}

function get_player_wagers($player){
    $wagers = array();
    foreach ($player["wager_requests"] as $wager_data)
        $wagers[] = $wager_data["py/state"];
    return $wagers;  
}

function get_avatar_url($player){
    $image_name = "../imagecache/httpscdndiscordappcomavatars*".$player['id']."*";
    foreach (glob($image_name) as $image_found) {
        return $image_found;
    }
    return null;
}
?>
