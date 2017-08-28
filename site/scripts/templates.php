<?php

require_once("templatesystem.php");
require_once("players.php");
require_once("auth.php");
require_once("util.php");
require_once("weapons.php");

define("DEFAULT_IMAGE","../img/missingimg.png");


/*
 * Templates.
 * Idk if $this is any good but it gets the HTML
 * out of the PHP files.
 */

class StaticContent extends Template
{
    private $no_template = False;
    private $static_content_string = "";

    function __construct($static_file_or_string) {
        parent::__construct('../templates/'.$static_file_or_string);
        if (!file_exists('../templates/'.$static_file_or_string)){
            $this->no_template = true;
            $this->add_content($static_file_or_string);
        }
    }

    // I'm not going to block no static stuff here
    // but don't.
    public function add_content($content){
        if (is_string($content))
            $this->static_content_string .= $content."\n";
        else if ($content instanceof Template)
            $this->static_content_string .= $content->output();
        $this->set_value('static',$this->static_content_string);
    }

    // static is to allow an array of strings to be output
    // without them all needing templates or changes to
    // the old code.
    protected function template_contents()
    {
        if (!$this->no_template)
            return parent::template_contents();
        else
            return "[@static]";
    }
}


class StringTemplate extends Template
{
    private $template_contents;
    
    function __construct($template_contents)
    {
        parent::__construct(null);
        $this->template_contents = $template_contents;
    }
    
    protected function template_contents()
    {
      return $this->template_contents;
    }
}


class Box extends Template 
{
    function __construct($content) {
        parent::__construct('../templates/box.tpl');
        $this->set_value('content',$content);
    }
}


class Sidebar extends Template
{
   private $sidebar_content;

   function __construct($sidebar_content) {
       parent::__construct('../templates/sidebar.tpl');
       $this->sidebar_content = $sidebar_content;
       $this->set_value('content',$sidebar_content);
   }

   public function append_content($content)
   {
     $this->sidebar_content[] = $content;
     $this->set_value('content',$this->sidebar_content);
   }

   public function prepend_content($content)
   {
     $this->sidebar_content = array_unshift($sidebar_content,$content);
     $this->set_value('content',$this->sidebar_content);
   }

   public function get_content()
   {
     return $this->sidebar_content;
   }
}

class CommandBox extends Template
{
   function __construct($name = "", $help = "", $perm_icon ="", $perm_colour = "#95d3bd", $perm_message = "") {
      parent::__construct('../templates/command_box.tpl');
      $this->set_value('commandname',$name);
      $this->set_value('help',$help);
      $this->set_value('permicon',$perm_icon);
      $this->set_value('permcolour',$perm_colour);
      $this->set_value('permmessage',$perm_message);
   }
}

class User extends Template
{
   function __construct($player, $avatar, $auth_url = null) {
       if (is_null($auth_url)) {
           parent::__construct('../templates/user.tpl');
           $this->set_value('level', $player["level"]);
           $this->set_value('name', htmlspecialchars($player["name"]));
           $this->set_value('avatar', $avatar);
       } else {
           parent::__construct('../templates/userlogin.tpl');
           $this->set_value('authurl', htmlspecialchars($auth_url));
           $this->set_value('avatar', DEFAULT_AVATAR);
       }
   }
}

class Link extends Template
{
    function __construct($link_name,$link) {
        parent::__construct('../templates/navigationlink.tpl');
        $this->set_value('linkname',$link_name);
        $this->set_value('link',htmlspecialchars($link));
    }
}

class Navigation extends Template
{
    function __construct($title,$links){
        parent::__construct('../templates/navigation.tpl');
        $this->set_value('title',$title);
        $this->set_links($links);
    }

    private function set_links($links){
        $nav_links = array();
        foreach ($links as $link_name => $link)
            $nav_links[] = new Link($link_name,$link);
        $this->set_value('links',$nav_links);
    }
}


abstract class Layout extends Template
{
    private $header;
    private $body;

    function __construct($page_name,$sidebar,$content_title,$content,$header_buttons = array(),$body = array()) {
        parent::__construct('../templates/layout.tpl');
        $auth = get_auth();
        if(!is_array($body))
            $this->body = array($body);
        if ($auth['login']) {
            $header_buttons[] = new StaticContent("../templates/addtionalheaderactions.tpl");
            $user_id = get_user_details()['id'];
            $this->body[] = new SettingsPopup(is_profile_private($user_id), $user_id);
        }
        // Add invite menu to layout if blank
        if (isset($_SESSION["userId"]))
        {
            require_once("invites.php");
            require_once("../php/groups.php");
            $header_buttons[] = getInviteMenuList();
        }
        $this->set_value('headerbuttons',$header_buttons);
        $this->set_value('pagename',$page_name);
        $this->set_value('sidebar',$sidebar);
        $this->set_value('contenttitle',$content_title);
        $this->set_value('content',$content);
        $this->set_value('body',$this->body);
        $this->set_value('header',"");
        $this->set_value('flexstyle', "page-content");
    }

    protected function set_header($value){
        if (!isset($this->header))
            $this->header = new StaticContent($value);
        else
            $this->header->add_content($value);
        $this->set_value('header',$this->header);
    }

    function set_css($css){
        $this->set_header("<link rel=\"stylesheet\" href=\"$css\" />");
    }

    function set_script($script){
        $this->set_header("<script src=\"$script\"></script>");
    }
    
    function set_meta($properties){
        $tags = "";
        foreach($properties as $name => $value)
            $tags .= " $name=\"$value\"";
        $this->set_header("<meta$tags/>");
    }
    
    function body_append($object) {
        $this->body[] = $object;
        $this->set_value('body',$this->body);
    }
}

class SettingsPopup extends Template 
{
    function __construct($private_profile, $player_id) {
        parent::__construct('../templates/settingspopup.tpl');
        $this->set_value('checked', $private_profile ? '' : 'checked');
        $this->set_value('playerid', $player_id);
    }
}

class HomePageContent extends Template
{
    function __construct($topdog, $topdog_count, $server_invite, $bot_invite) {
        parent::__construct('../templates/content_home.tpl');
        $this->set_value('topdog',htmlspecialchars($topdog['name']));
        $this->set_value('topdogid',htmlspecialchars($topdog['id']));
        $this->set_value('topdogcount',$topdog_count);
        $this->set_value('serverinvite', htmlspecialchars($server_invite));
        $this->set_value('botinvite', htmlspecialchars($bot_invite));
    }

}

class CommandList extends Template
{
    function __construct($name, $command_list) {
        parent::__construct('../templates/command_list.tpl');
        $this->set_value('listname',$name);
        $this->set_value('commands',$command_list);
    }  
}


abstract class LogBox extends Template {
    protected $listitems = array();

    function __construct($template){
        parent::__construct("../templates/$template.tpl");
        $this->set_value('logrows',"");
        $this->set_value('message',"");
    }

    abstract public function add_row(...$row_args);
}

class Leaderboard extends LogBox {

    function __construct(){
        parent::__construct('leaderboard');
    }

    public function add_row(...$player_details){
        // Player + Ranking
        $this->listitems[] = new LeaderboardRow($player_details[0], $player_details[1]);
        $this->set_value('logrows', $this->listitems);
    }    
    
}

class LeaderboardRow extends Template {
    function __construct($player, $rank){
        parent:: __construct('../templates/leaderboardrow.tpl');
        $this->set_value('playername',htmlspecialchars($player["name"]));
        $this->set_value('playerid',htmlspecialchars($player["id"]));
        $this->set_value('totalexp',intval($player["total_exp"]));
        $this->set_value('rank', $rank);
        $this->set_value('level',$player['level']);
        $this->set_value('avatar',get_avatar_url($player));
    }  
}

class QuestLog extends LogBox
{
    function __construct() {
        parent::__construct('questlog');
    }
    
    public function add_row(...$quest_details){
        $this->listitems[] = new QuestRow(...$quest_details);
        $this->set_value('logrows', $this->listitems);
    }
}

class QuestRow extends Template {
  
    function __construct($active_quest ,$quest ,$reward, $weapon, $quest_index) {
        parent::__construct('../templates/questrow.tpl');
        $image_path = get_cached_image_from_url($quest['image_url']);
        if (!is_null($image_path)) {
            $this->set_value('image', $image_path);
        } else {
            $this->set_value('image', DEFAULT_IMAGE);
        }
        $this->set_value('level',$active_quest['level']);
        $this->set_value('questname', htmlspecialchars($active_quest['name']));
        $this->set_value('attack', round($active_quest['attack'], 2));
        $this->set_value('strg', round($active_quest['strg'], 2));
        $this->set_value('weapon', htmlspecialchars($weapon["name"]));
        $this->set_value('reward', number_format($reward));
        $this->set_value('accy',round($active_quest['accy'], 2));
        $this->set_value('questindex',$quest_index);
    }
}

class WeaponBox extends LogBox
{
    private $set_equipped = False;
    
    function __construct() {
        parent::__construct('myweapons');
    }
    
    public function add_row(...$weapon_details){
        if (sizeof($weapon_details) == 1) {
            $weapon = $weapon_details[0];
            if (!$this->set_equipped) {
                $this->set_value('equippedimage', get_weapon_image($weapon));
                $this->set_value('equippedname', htmlspecialchars($weapon['name']));
                $this->set_value('damage', $weapon['damage']);
                $this->set_value('accy', $weapon['accy']*100);
                $this->set_equipped = True;
            } else {
                $this->listitems[] = new Weapon($weapon);
            }
        } else {
            $this->listitems[] = new StaticContent('weaponslot.tpl');
        }
        $this->set_value('logrows', $this->listitems);
    }
}

class Weapon extends Template{
  
    function __construct($weapon)
    {
        parent::__construct('../templates/weapons.tpl');
        $this->set_value('image', get_weapon_image($weapon));
        $this->set_value('name', htmlspecialchars($weapon['name']));
        $this->set_value('damage', $weapon['damage']);
        $this->set_value('accy', $weapon['accy']*100);
        $this->set_value('hitmessage', htmlspecialchars($weapon['hit_message']));
    }
}

class StandardLayout extends Layout
{
   function __construct($sidebar,$content = "",$title, $page_desc, $title_override=null, $header_buttons = ""){
       parent::__construct(is_null($title_override) ? strip_tags($title) : $title_override,
                           $sidebar, $title, $content, $header_buttons);
       $this->set_base_url("http://$_SERVER[HTTP_HOST]/".end(explode('/',getcwd())).'/');
       $this->set_script("../js/general.js");
       $auth = get_auth();
       if ($auth['login']) {
          $this->set_value('dropdownoption','<a href="../logout/" class="mdl-menu__item"><li>Logout</li></a>');
       } else {
          $this->set_value('dropdownoption','<a href="'.htmlspecialchars($auth['authURL']).'" class="mdl-menu__item"><li>Login</li></a>');
       }
       $this->set_value('pagedesc', $page_desc);
   }
   
   function set_base_url($base) {
       $this->set_header("<BASE href=\"$base\">");
   }
}

class PlayerInfoHeader extends Template
{
    function __construct($player){
        parent::__construct('../templates/playerinfoheader.tpl');
        require_once("gamerules.php");
        $exp_for_next_level = get_exp_for_next_level($player['level']);
        $progess = $player['exp']/$exp_for_next_level * 100;
        $this->set_value('progress', $progess);
        $this->set_value('expneeded', intval($exp_for_next_level - $player['exp']));
        $this->set_value('nextlevel', $player['level'] + 1);
        $this->set_value('attack', round($player['attack'], 2));
        $this->set_value('strg', round($player['strg'], 2));
        $this->set_value('accy', round($player['accy'], 2));

    }
}

class ErrorPage extends StandardLayout {
    
    function __construct($sidebar, $error, $image, $message){
        parent::__construct($sidebar,
                            new _ErrorPageMessage($error, $image, $message), 
                                                  "<h2>$error</h2>", $error);
    }
}

class _ErrorPageMessage extends Template {
    function __construct($error, $image, $message)
    {
        parent::__construct('../templates/errorpage.tpl');
        $this->set_value('error', $error);
        $this->set_value('image', $image);
        $this->set_value('message', $message);
    }
}

class Error404Page extends ErrorPage {
    function __construct($sidebar) {
        header("HTTP/1.0 404 Not Found");
        parent::__construct($sidebar, '404', 'olddue.png', 'Just like the old bot your request could not be found!');
    }
}

class PrivatePage extends ErrorPage {
    function __construct($sidebar) {
        parent::__construct($sidebar, 'Private', 'private.png', 'This user has their profile set as private!');
    }
}

class NotPlayerPage extends ErrorPage {
    function __construct($sidebar) {
        parent::__construct($sidebar, 'You\'re not a player!', 'noplayer.png', 'To view you\'re dashboard join a server with DueUtil!');
    }
}

class ComingSoonPage extends ErrorPage {
    function __construct($sidebar) {
        parent::__construct($sidebar, 'Coming soon!', 'comingsoon.png', 'This page has yet to be completed.');
    }
}

class NoThingsFound extends Template
{
    function __construct($title, $message, $prefix='You don\'t', $template_override=null)
    {
        if (is_null($template_override)) {
            parent::__construct('../templates/nothings.tpl');
        } else {
            parent::__construct('../templates/'.$template_override);
        }
        $this->set_value('title', $title);
        $this->set_value('thing', $message);
        $this->set_value('prefix', htmlspecialchars($prefix));
    }
}

class MyAwards extends LogBox
{
    function __construct() {
        parent::__construct('myawards');
    }
    
    public function add_row(...$award_details){
        $this->listitems[] = new Award(...$award_details);
        $this->set_value('logrows', $this->listitems);
    }
  
}

class Award extends Template 
{
    function __construct($image, $name, $message, $special) {
        parent::__construct('../templates/award.tpl');
        $this->set_value('image', '../awards/'.$image);
        $this->set_value('name', $name);
        $this->set_value('message', $message);
        $this->set_value('type', $special ? 'special-award' : 'normal-award');
        $this->set_value('title', $special ? 'This is a special award!' : '');

    }
}

class MyWagers extends LogBox
{
    function __construct() {
        parent::__construct('mywagers');
    }
    
    public function add_row(...$wager_details){
        $this->listitems[] = new WagerRow(...$wager_details);
        $this->set_value('logrows', $this->listitems);
    }
  
}

class WagerRow extends Template
{
    function __construct($wager_index, $amount, $sender) {
        parent::__construct('../templates/wagerrow.tpl');
        $this->set_value('playername', htmlspecialchars($sender['name']));
        $this->set_value('avatar', get_avatar_url($sender));
        $this->set_value('level',$sender['level']);
        $this->set_value('playerid',htmlspecialchars($sender['id']));
        $this->set_value('wagerindex',$wager_index);
        $this->set_value('amount',$amount);

    }
  
}


class PartnerCard extends Template {
    
    function __construct($name, $type, $image, $message, $page, $link_name, $link) {
        parent::__construct('../templates/partner.tpl');
        $this->set_value('name', htmlspecialchars($name));
        $this->set_value('type', $type);
        $this->set_value('image', htmlspecialchars($image));
        $this->set_value('message', htmlspecialchars($message));
        $this->set_value('page', $page);
        $this->set_value('linkname', htmlspecialchars($link_name));
        $this->set_value('customlink', htmlspecialchars($link));
    }
}

class GenericThing extends Template {
    
    function __construct($template) {
          parent::__construct('../templates/'.$template);
    }
}

?>
