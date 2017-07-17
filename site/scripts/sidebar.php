<?php
require_once("../scripts/templates.php");
require_once("../scripts/auth.php");
require_once("../scripts/players.php");

/* The sidebar that does other stufff too */
unset($_SERVER['QUERY_STRING']);

$sidebar_content = array();
$auth = get_auth();

if (!$auth['login'] or !defined("NEEDS_AUTH")) {
    update_last_page();
} else {
    update_last_page('/home');
}

if (!$auth['login']) {
    $sidebar_content[] = new User(null, null, $auth['authURL']);
} else {
    $user_data = get_user_details();
    $avatar = $user_data['avatar'];
    $user_id = $user_data['id'];
    upsert('dueutiltechusers', $user_id, ['ip' => $_SERVER['REMOTE_ADDR']], $set_mode='$setOnInsert');
    if (!is_null($avatar)) {
        $avatar = "https://cdn.discordapp.com/avatars/$user_id/$avatar.jpg";
    } else {
        $avatar = DEFAULT_AVATAR;
    }
        
    $player = find_player($user_id);
    if (is_null($player)) {
        $sidebar_content[] = new User(array('name' => (trim($user_data['username'])),
                                            'level' => 1), $avatar);
    } else {
        $sidebar_content[] = new User($player, $avatar);  
    }
}

$sidebar_content[] = new Navigation('General',
                                    array(
                                      'DueUtil' => '../home',
                                      'How To Guide'=>'../howto',
                                      'Commands'=>'../commands',
                                      'Leaderboard'=>'../leaderboard'
                                    ));                                  
$sidebar_content[] = new Navigation('Tools',
                                    array(
                                      'MyDashboard' => '../mydash',
                                      'The Shop' => '../soon',
                                      'Quest Builder'=>'../soon',
                                      'Weapon Builder'=>'../soon',
                                      'Upgrader'=>'../soon'
                                    ));

$sidebar = new Sidebar($sidebar_content);
?>
