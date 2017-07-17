<?php
require_once("../scripts/util.php");
$page = strtok($_SERVER["REQUEST_URI"], '?');
// TODO Change
$player_page = startsWith($page, '/dueutil/player/'); // /player/ page or /mydash/ page
if (!$player_page)
    require_once("../scripts/needsauth.php");
else
    require_once("../scripts/sidebar.php");
require_once("../scripts/dbconn.php");
require_once("../scripts/players.php");
require_once("../scripts/quests.php");
require_once("../scripts/weapons.php");


/*
 * Player dash/profile
 */

if ($player_page) {
    if (isset($_GET["id"])) {
        $player_id = $_GET["id"];
        if (is_numeric($player_id))
            $player = find_player($_GET["id"]);
        else
            $player = null;
    }
    if (!isset($_GET["id"]) || is_null($player)) {
        (new Error404Page($sidebar))->show();
        die();
    } else if (is_profile_private($player['id'])) {
        (new PrivatePage($sidebar))->show();
        die();
    }
} else {
    $player_id = $user_data["id"];
    $player = find_player($player_id);
    if (is_null($player)) {
        (new NotPlayerPage($sidebar))->show();
        die();
    }
}

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
    // TODO you don't to X does not for public profile.
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

// Wagers
$wager_requests = get_player_wagers($player);
if (sizeof($wager_requests) > 0) {
    $wagers = new MyWagers();
    foreach ($wager_requests as $wager_index => $wager_request) {
        $sender = find_player($wager_request['sender_id']);
        $wagers->add_row($wager_index + 1, $wager_request['wager_amount'], $sender);
    }
  } else{
    $wagers = new NoThingsFound("Wager requests", "wager requests right now");
}

// Awards - TODO

// Adding content
$content = array();
$content[] = new PlayerInfoHeader($player);
$content[] = $active_quests;
$content[] = $weapons;
$content[] = new StaticContent('<div style="width:100%"></div>');
$content[] = $wagers;
$content[] = new MyAwards();

// Create page
$page = new StandardLayout($sidebar,$content,$title = "<h2>".htmlspecialchars($player["name"])."</h2>");

// Scripts and CSS
$page->set_css('../css/due-style-tables.css');
$page->set_script('../js/logs.js');
$page->set_script('./dash.js');

$page->show();
?>
