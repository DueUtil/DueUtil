<?php
require_once("auth.php");

define("NEEDS_AUTH", True);

// Kinda a hack
require_once("sidebar.php");

$auth = get_auth();

if (!$auth['login'])
{
    header('Location: '.$auth['authURL']);
    die();
}
// TODO change
?>
