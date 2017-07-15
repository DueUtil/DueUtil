<?php
require_once("../scripts/dbconn.php");
require_once("../scripts/util.php");
require_once("../scripts/weapons.php");


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


function get_player_weapons($player) {
    global $NO_WEAPON;
    $equipped = get_weapon_by_id($player['equipped']['weapon']);
    $stored = array();
    foreach($player['inventory']['weapons'] as $weapon_id) {
        $weapon = get_weapon_by_id($weapon_id);
        if ($weapon == $NO_WEAPON)
            continue;
        $stored[] = $weapon;
    }
    array_unshift($stored, $equipped);
    $all_weapons = $stored;
    return $all_weapons;
}
?>
