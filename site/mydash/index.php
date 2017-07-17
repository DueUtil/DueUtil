
<?php
require_once ("../scripts/util.php");

$page = strtok($_SERVER["REQUEST_URI"], '?');
$player_page = startsWith($page, '/player'); // /player/ page or /mydash/ page

if (!$player_page) {
    // We only need auth if this is mydash.
    require_once ("../scripts/needsauth.php");
}
else {
    require_once ("../scripts/sidebar.php");
}

require_once ("../scripts/dbconn.php");
require_once ("../scripts/players.php");
require_once ("../scripts/quests.php");
require_once ("../scripts/weapons.php");
require_once ("../scripts/awards.php");

/*
* Player dash/profile
*/

// Switching between mydash and player profile.
if ($player_page) {
    // Public profile page.
    // Get ID from query string.
    if (isset($_GET["id"])) {
        $player_id = $_GET["id"];
        // Ensure it's a discord id (just numeric)
        if (is_numeric($player_id)) {
            // Fetch player data (can return null)
            $player = find_player($_GET["id"]);
        }
        else {
            // Make player null (so 404 shows)
            $player = null;
        }
    }
    if (!isset($_GET["id"]) || is_null($player)) {
        // Show a fake 404 page
        (new Error404Page($sidebar))->show();
        die();
    }
    else if (is_profile_private($player['id'])) {
        // Private page (they need to set their profile public)
        (new PrivatePage($sidebar))->show();
        die();
    }
    // Prefix from 'you' to 'name does'
    $no_items_preix = $player['name'] . ' does not';
}
else {
    // MyDashboard page
    $player_id = $user_data["id"];
    // Get logged in user.
    $player = find_player($player_id);
    if (is_null($player)) {
        // They don't playe DueUtil.
        (new NotPlayerPage($sidebar))->show();
        die();
    }
    // You prefix (since only the logged in user can see this)
    $no_items_preix = 'You don\'t';
}

// Quests
$player_quests = get_player_quests($player);
$quest_count = sizeof($player_quests);
if (sizeof($player_quests) > 0) {
    // They have quests
    $active_quests = new QuestLog();
    foreach(array_reverse($player_quests) as $index => $active_quest) {
        $quest = get_quest($active_quest["q_id"]);
        if (is_null($quest)) {
            $quest = array(
                'image_url' => DEFAULT_AVATAR
            );
        }
        $active_quests->add_row($active_quest, $quest, get_quest_reward($active_quest, $player) , get_weapon_by_id($active_quest['equipped']['weapon']) , $quest_count - $index);
    }
}
else {
    // They don't have quests
    $active_quests = new NoThingsFound('Active quests', 'quests right now', $no_items_preix);
}

// Weapons
$weapons = new WeaponBox();
$player_weapons = get_player_weapons($player);
foreach($player_weapons as $weapon) {
    // Add the weapon details
    $weapons->add_row($weapon);
}
for ($placeholder = 0; $placeholder < 7 - sizeof($player_weapons); $placeholder++) {
    // Add empty weapon slots
    $weapons->add_row();
}

// Wagers
$wager_requests = get_player_wagers($player);
if (sizeof($wager_requests) > 0) {
    $wagers = new MyWagers();
    foreach($wager_requests as $wager_index => $wager_request) {
        $sender = find_player($wager_request['sender_id']);
        $wagers->add_row($wager_index + 1, $wager_request['wager_amount'], $sender);
    }
}
else {
    $wagers = new NoThingsFound('Wager requests', 'wager requests right now', $no_items_preix);
}

// Awards - TODO
$player_awards = $player['awards'];
if (sizeof($player_awards) > 0) {
    $awards_list = new MyAwards();
    foreach(array_reverse($player_awards) as $award_id) {
        $awards_detail = get_award_details($award_id);
        $awards_list->add_row($awards_detail['icon'], $awards_detail['name'], $awards_detail['message']);
    }
} else {
    $awards_list = new StaticContent('noawards.tpl');
}

// Adding content
$content = array();
$content[] = new PlayerInfoHeader($player);
$content[] = $active_quests;
$content[] = $weapons;
$content[] = new StaticContent('<div style="width:100%"></div>');
$content[] = $wagers;
$content[] = $awards_list;

// Create page
$page = new StandardLayout($sidebar, $content, $title = '<h2>' . htmlspecialchars($player['name']) . '</h2>');

// Scripts and CSS
$page->set_css('../css/due-style-tables.css');
$page->set_script('../js/logs.js');
$page->set_script('../js/dash.js');
$page->show();
?>
