<?php
require_once("auth.php");

$auth = get_auth();

if (!$auth['login'])
{
    header('Location: '.$auth['authURL']);
    die();
}
?>
