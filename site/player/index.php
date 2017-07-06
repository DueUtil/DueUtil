<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/dbconn.php");


/*
 * Player page
 */


# TODO Check it it really is a discord id
$player_id = $_GET["player"];


$find_player_query = new MongoDB\Driver\Query(array('_id' => $player_id));

$cursor = $manager->executeQuery('dueutil.Player',$find_player_query );
# TODO Handle not found
$data = "data";
$player_data = $cursor->toArray()[0]->$data;
// We're translating from python pickled data
$player = json_decode($player_data, True)["py/state"];
// Show dashboard.    
// Will be Quest log, weapons, wagers, inventory
$content = array(new QuestLog(),new QuestLog(),new QuestLog(),new QuestLog());
$page = new StandardLayout($sidebar,$content,$title = "<h2>".htmlspecialchars($player["name"])
                                                ." (".$player["id"].")</h2>");
$page->set_css('../css/due-style-tables.css');
$page->show();
                                                
                                         


?>
