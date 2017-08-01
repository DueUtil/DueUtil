<?php
require_once("../scripts/discordstuff.php");
require_once("../scripts/constants.php");


$embed = new Embed($title="This is a test!", $color=0);
$embed->add_field($name="Test", $value="This is some text!");
$embed->set_footer($text="This is a footer");
$embed->set_image($url="https://i.redditmedia.com/dTDcLwqLE9wmwUGhCb6dKE8rGbCCBbdXJJjO2iTBl28.jpg?w=732&s=e7f0760d1c00f691dde7eb3f66e1c92e");
$embed->set_thumbnail($url="https://i.redditmedia.com/dTDcLwqLE9wmwUGhCb6dKE8rGbCCBbdXJJjO2iTBl28.jpg?w=732&s=e7f0760d1c00f691dde7eb3f66e1c92e");
$embed->set_author($name="dueutil.tech",$url="https://dueutil.tech/home/");
$embed->set_provider($name="DueUtil",$url="https://dueutil.tech/home/");


send_webhook(PARTNER_WEBHOOK, array('embeds'=>[$embed]));

?>
