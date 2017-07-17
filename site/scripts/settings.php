<?php
require_once("players.php");
require_once("auth.php");

var_dump($_POST);
$auth = get_auth();

if ($auth['login'] && $_POST['public-profile']) {
    set_profile_privacy(get_user_details()['id'], False);
}

?>
