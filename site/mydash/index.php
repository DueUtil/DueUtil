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

$active_quests = new QuestLog();

foreach (array_reverse(get_player_quests($player)) as $active_quest) {
  $quest = get_quest($active_quest["q_id"]);
  if (is_null($quest))
      $quest = array('image_url' => DEFAULT_AVATAR);
  $active_quests->add_row($active_quest, $quest, 
                          get_quest_reward($active_quest, $player), 
                          get_weapon_by_id($active_quest["equipped"]["weapon"]));
}

// Show dashboard.    
// Will be Quest log, weapons, wagers, inventory
$content = array();

$content[] = $active_quests;

$page = new StandardLayout($sidebar,$content,$title = "<h2>".htmlspecialchars($player["name"])."</h2>");
$page->set_css('../css/due-style-tables.css');
$page->set_script('../js/logs.js');

$page->show();
?>
