<?php
require_once("../scripts/dbconn.php");
require_once("../scripts/util.php");


function find_player($player_id)
{
    return get_object($player_id,'Player');
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
    return get_cached_image($image_name);
}
?>
