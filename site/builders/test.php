<?php
require_once("../scripts/discordstuff.php");

define("BUILDER_WEBHOOK", "https://discordapp.com/api/webhooks/342073632412925952/AVf6YzBLrjsj979ouriyA2obtAAwJWH1ZcsTBL7hw9KSJdGhCNNRg6JvpEHCtfQeXjXO");

send_webhook(BUILDER_WEBHOOK, array("content"=>'!createquest_for 213007664005775360 132315148487622656 "Snek Man" 1.3 2 1.1 32 "Kill the" "Dagger" http://i.imgur.com/sP8Rnhc.png 21'));


?>
