<?php
require_once("../scripts/dbconn.php");
require_once("../scripts/util.php");
require_once("../scripts/weapons.php");


function get_quest($quest_id)
{
    return get_object($quest_id,'Quest');
}


function get_quest_reward($quest, $quester)
{
    $base_reward = $quest["cash_iv"] * $quest["level"];
    return max(1, intval($base_reward + $base_reward * (get_quest_scale($quest, $quester)+1)*10));
}


function get_quest_scale($quest, $quester)
{
    $avg_stats = get_avg_stats($quest);
    $quest_weapon = get_weapon_by_id($quest["equipped"]["weapon"]);
    $quester_weapon = get_weapon_by_id($quester["equipped"]["weapon"]);
    $hp_difference = ($quest["hp"] - $quester["hp"]) / $quest["hp"] / 10;
    $stat_difference = ($avg_stats - get_avg_stats($quester)) / $avg_stats;
    $weapon_damage_difference = ($quest_weapon["damage"] - $quester_weapon["damage"]) / $quest_weapon["damage"];
    $weapon_accy_difference = ($quest_weapon["accy"] - $quester_weapon["accy"]) / $quest_weapon["accy"];
    return ($stat_difference * 10 + $weapon_damage_difference/3 + $weapon_accy_difference * 5 + $hp_difference * 5)/20;
}




?>
