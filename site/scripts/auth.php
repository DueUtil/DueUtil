<?php
require_once __DIR__ . '/../vendor/autoload.php';

define("CLIENT_ID","212707063367860225");
define("CLIENT_SECRET","GoP6T87FuwLltuKrZdbH1eGnEpUbhDG1");
define("REDIRECT_URL","http://localhost/home");

session_name('dueutil_tech_auth');

$auth_scopes = ['identify','guilds',];

$provider = new \Discord\OAuth\Discord([
	'clientId'     => CLIENT_ID,
	'clientSecret' => CLIENT_SECRET,
	'redirectUri'  => REDIRECT_URL,
]);

session_start();

if (isset($_GET['code']) && !isset($_SESSION['access_token'])){
    $token = $provider->getAccessToken('authorization_code', [
      'code' => $_GET['code'],
    ]);
    $_SESSION['access_token'] = $token;
    
    redirect();
} else if (isset($_SESSION['access_token'])) {
    check_auth();
}


function check_auth() {
  global $provider;

  if (isset ($_SESSION['access_token'])) {
      try {
          $provider->getResourceOwnerDetailsUrl($_SESSION['access_token']);
      } catch (DiscordRequestException $e) {
          $refresh = $provider->getAccessToken('refresh_token', [
                                               'refresh_token' => $getOldTokenFromMemory->getRefreshToken(),]);
          $_SESSION['access_token'] = $refresh;
          
          try {
              $provider->getResourceOwnerDetailsUrl($_SESSION['access_token']);
          } catch (DiscordRequestException $e) {
              logout();
          }
      }
  }
}


function get_user_details(){
    global $provider;
    check_auth();
    if (isset($_SESSION['access_token']))
        return $provider->getResourceOwner($_SESSION['access_token'])->toArray();
    else
        return null;
}


function update_last_page($url = null) {
    if (isset($_COOKIE["dueutil_tech_redirect"])) {
        unset($_COOKIE["dueutil_tech_redirect"]);
        setcookie('dueutil_tech_redirect', '', time() - 3600);
    }
    if (is_null($url))
        $url = $_SERVER['REQUEST_URI'];
    setcookie('dueutil_tech_redirect', "http://$_SERVER[HTTP_HOST]$url", time()+3600, '/');
}



function get_auth() {
  global $provider, $auth_scopes;
  
  check_auth();
  if (!isset($_SESSION['access_token'])) {
      // TODO: Domain
      return array('login' => False, 'authURL' => $provider->getAuthorizationUrl(array('scope' => $auth_scopes)));
  } else {
      return array('login' => True, 'token' => $_SESSION['access_token']);
  }
}


function redirect() {
  if (isset($_COOKIE["dueutil_tech_redirect"])) {
    header('Location: '.$_COOKIE["dueutil_tech_redirect"]);
    //var_dump($_COOKIE["dueutil_tech_redirect"]);
    die();
  }
}


function logout() {
  session_destroy();
  redirect();
}
?>
