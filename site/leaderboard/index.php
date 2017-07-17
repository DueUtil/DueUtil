<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/dbconn.php");
require_once("../scripts/players.php");
require_once("../scripts/util.php");


/*
 * Leaderboard
 */
 

$start_rank = 1;

$find_players = new \MongoDB\Driver\Query(
        [], // query (empty: select all)
        [ 'sort' => [ 'rank' => $start_rank ], 'limit' => 10 ]
);

// Find in player leaderboard
$cursor = $manager->executeQuery('dueutil.levels', $find_players); 
$leaderboard_data = $cursor->toArray();
$leaderboard = new Leaderboard();

if (sizeof($leaderboard_data) == 0){
  $leaderboard->set_value('message','<div class="log-bg" style="width: calc(100% -12px); margin-top:0px; padding: 12px">'
                                    .'No leaderboard data! Please check back later!</div>');
} else {
    foreach ($leaderboard_data as $player_rank) {
        $player_rank = object_to_array($player_rank);
        $player = find_player($player_rank['player_id']);
        $leaderboard->add_row($player,$player_rank['rank']);
    }
}
 
$page = new StandardLayout($sidebar,$leaderboard ,$title = "<h2>Global Leaderboard</h2>", "DueUtil global leaderboard!");

$page->set_css('../css/due-style-tables.css');
$page->show();

?>
