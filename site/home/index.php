<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/dbconn.php");
require_once("../scripts/players.php");
require_once("../scripts/util.php");
require_once("../scripts/constants.php");

/*
 * The home page
 */
 
$find_topdog_query = new MongoDB\Driver\Query(array('award' => 'TopDog'));
$cursor = $manager->executeQuery('dueutil.award_stats',$find_topdog_query);
$topdog_data = $cursor->toArray();
if (sizeof($topdog_data) == 1) {
  $topdog_stats = object_to_array($topdog_data[0]);
  if (array_key_exists('top_dog',$topdog_stats))
  {
      $top_dog = find_player($topdog_stats['top_dog']);
      $top_dog_count = $topdog_stats['times_given'];
  }
}

// TODO: No topdog

// Show dashboard.
(new StandardLayout($sidebar,new HomePageContent($top_dog,int_to_ordinal($top_dog_count),
                             SERVER_INVITE,BOT_INVITE), "<h2>DueUtil</h2>",
                             "DueUtil the questing and fun discord bot!", 
                             "The Worst Discord Bot"))->show();
?>
