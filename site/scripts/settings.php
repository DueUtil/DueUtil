<?php
require_once("players.php");
require_once("auth.php");

$auth = get_auth();
if ($auth['login']) {
    if (isset($_POST['public-profile'])) {
        // Public profile
        set_profile_privacy(get_user_details()['id'], False);
    } else {
        // Private profile
        set_profile_privacy(get_user_details()['id'], True);
    }
} else {
    echo "Unauthorized";
    http_response_code(401);
    die();
}

?>
