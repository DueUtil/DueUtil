<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/dbconn.php");
require_once("../scripts/players.php");
require_once("../scripts/util.php");

/*
 * The home page
 */
 
define("SERVER_INVITE","https://discord.gg/n4b94VA");
define("BOT_INVITE","https://discordapp.com/oauth2/authorize?client_id=213271889760616449&scope=bot&permissions=268553280");


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
(new StandardLayout($sidebar,new HomePageContent($top_dog,int_to_ordinal($top_dog_count),SERVER_INVITE,BOT_INVITE)))->show();
?>
