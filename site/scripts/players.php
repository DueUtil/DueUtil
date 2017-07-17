<?php
require_once("../scripts/dbconn.php");
require_once("../scripts/util.php");
require_once("../scripts/weapons.php");


define("DEFAULT_AVATAR","../img/avatardue.png");


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
    return $player["received_wagers"];  
}


function get_avatar_url($player){
    $image_name = "../imagecache/httpscdndiscordappcomavatars*".$player['id']."*";
    $avatar = get_cached_image($image_name);
    if (!is_null($avatar)) 
        return $avatar;
    else
        return DEFAULT_AVATAR;
}


function is_profile_private($player_id){
    global $manager;
    $find_private_option = new MongoDB\Driver\Query(array('_id' => $player_id));
    $cursor = $manager->executeQuery('dueutil.public_profiles', $find_private_option);
    $private_record = $cursor->toArray();
    if (sizeof($private_record) == 0)
        return True;
    else
        return $private_record[0]->private;
}


function set_profile_privacy($player_id, $private){
    global $manager;
    // TODO upsert
    $bulk = new MongoDB\Driver\BulkWrite;
    $private_record = ['_id' => $player_id, 'private' => $private];
    $bulk->insert($private_record);
    $write_concern = new MongoDB\Driver\WriteConcern(MongoDB\Driver\WriteConcern::MAJORITY, 1000);
    $result = $manager->executeBulkWrite('dueutil.public_profiles', $bulk, $write_concern);
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
