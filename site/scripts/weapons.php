<?php
require_once("util.php");


define("NONE_WEAPON_IMAGE","http://i.imgur.com/gNn7DyW.png");
define("DEFAULT_WEAPON_IMAGE","http://i.imgur.com/QFyiU6O.png");
define("PRICE_CONSTANT",0.04375);



$NO_WEAPON = create_weapon("None", "None", 1, 0.66, "🗡", True, NONE_WEAPON_IMAGE);
$DAGGER = create_weapon("Dagger", "stabs", 10, 0.285, ":dagger:", True, DEFAULT_WEAPON_IMAGE);

function create_weapon($name, $hit_message, $damage, $accy, $icon, $melee, $image_url)
{
  $price = intval($accy * $damage / PRICE_CONSTANT) + 1;
  $weapon_sum = sprintf("%d|%d|%.2f", $price, $damage, $accy);
  $id = sprintf("%s+%s/%s", "STOCK", $weapon_sum, strtolower($name));
  
  return array('id' => $id,
                       'name' => $name,
                       'accy' => $accy,
                       'damage' => $damage, 
                       'price' => $price,
                       'icon' => $icon,
                       'hit_message' => $hit_message,
                       'melee' => $melee,
                       'image_url' => $image_url,
                       'weapon_sum' => $weapon_sum);
}


function get_weapon_by_id($weapon_id){
    global $NO_WEAPON, $DAGGER;
    
    if (strcmp($weapon_id, $DAGGER["id"]) == 0)
        return $DAGGER;
    $weapon = get_object($weapon_id, 'Weapon');
    if (!is_null($weapon))
        return $weapon;
    return $NO_WEAPON;
}


function get_weapon_image($weapon) {
    $image_path = get_cached_image_from_url($weapon['image_url']);
    if (!is_null($image_path)) {
        return $image_path;
    }
    return DEFAULT_WEAPON_IMAGE;
}


?>
