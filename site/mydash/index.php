<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/needsauth.php");
require_once("../scripts/dbconn.php");
require_once("../scripts/players.php");
require_once("../scripts/quests.php");
require_once("../scripts/weapons.php");


/*
 * Player dash
 */


# TODO Check it it really is a discord id
$player_id = $user_data["id"];

$player = find_player($player_id);

// TODO player null.
if (is_null($player))
    die();

// Quests
$player_quests = get_player_quests($player);
$quest_count = sizeof($player_quests);
if (sizeof($player_quests) > 0) {
    $active_quests = new QuestLog();
    foreach (array_reverse($player_quests) as $index => $active_quest) {
      $quest = get_quest($active_quest["q_id"]);
      if (is_null($quest))
          $quest = array('image_url' => DEFAULT_AVATAR);
      $active_quests->add_row($active_quest, $quest, 
                              get_quest_reward($active_quest, $player), 
                              get_weapon_by_id($active_quest["equipped"]["weapon"]),
                              $quest_count - $index);
    }
} else {
    $active_quests = new NoThingsFound("Active quests","quests right now");
}

// Weapons
$weapons = new WeaponBox();
$player_weapons = get_player_weapons($player);
foreach($player_weapons as $weapon)
    $weapons->add_row($weapon);
for ($placeholder = 0; $placeholder < 7 - sizeof($player_weapons); $placeholder++) {
    $weapons->add_row();
}

$content = array();
$content[] = new PlayerInfoHeader($player);
$content[] = $active_quests;
$content[] = $weapons;
$content[] = new StaticContent('<div style="width:100%"></div>');
$content[] = new MyWagers();
$content[] = new WeaponBox();


$page = new StandardLayout($sidebar,$content,$title = "<h2>".htmlspecialchars($player["name"])."</h2>");
$page->set_css('../css/due-style-tables.css');
$page->set_script('../js/logs.js');
$page->set_script('./layout.js');

$page->show();
?>
