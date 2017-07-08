<?php
require_once("../scripts/templates.php");
require_once("../scripts/auth.php");

unset($_SERVER['QUERY_STRING']);

$sidebar_content = array();

$auth = get_auth();

if (!$auth['login']) {
    $sidebar_content[] = new User(null, $auth['authURL']);
} else {
    $token = $auth['token'];
    $user = $provider->getResourceOwner($token);
    $user_data = $user->toArray();
    $user_id = $user_data['id'];
    $avatar = $user_data['avatar'];
    if (!is_null($avatar))
        $avatar = "https://cdn.discordapp.com/avatars/$user_id/$avatar.jpg";
    else
        $avatar = DEFAULT_AVATAR;
    $sidebar_content[] = new User(array('name' => htmlspecialchars(trim($user_data['username'])),
                                        'id' => htmlspecialchars(trim($user_id)),
                                        'avatar' => $avatar));
}
$sidebar_content[] = new Navigation('General',
                                    array(
                                      'DueUtil' => '../home',
                                      'How To Guide'=>'#',
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
