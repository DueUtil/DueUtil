<?php
require_once("../scripts/templates.php");
require_once("../scripts/auth.php");
require_once("../scripts/players.php");


unset($_SERVER['QUERY_STRING']);

$sidebar_content = array();

$auth = get_auth();

if (!$auth['login']) {
    $sidebar_content[] = new User(null, null, $auth['authURL']);
} else {
    $token = $auth['token'];
    $user = $provider->getResourceOwner($token);
    $user_data = $user->toArray();
    $avatar = $user_data['avatar'];
    $user_id = $user_data['id'];
    if (!is_null($avatar))
        $avatar = "https://cdn.discordapp.com/avatars/$user_id/$avatar.jpg";
    else
        $avatar = DEFAULT_AVATAR;
        
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
                                      'Quest Builder'=>'#',
                                      'Weapon Builder'=>'#'
                                    ));
$sidebar = new Sidebar($sidebar_content);
?>
