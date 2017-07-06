<?php

require_once("templatesystem.php");
require_once("players.php");

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
   function __construct($user) {
       parent::__construct('../templates/user.tpl');
       $this->set_value('userid', $user["id"]);
       $this->set_value('name', $user["name"]);
       $this->set_value('avatar', $user["avatar"]);
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

    function __construct($page_name,$sidebar,$content_title,$content,$header_buttons = array(),$body = array()) {
        parent::__construct('../templates/layout.tpl');
        $header_buttons[] = new StaticContent("../templates/addtionalheaderactions.tpl");
        if(!is_array($body))
            $body = array($body);
        $body[] = new StaticContent("../templates/generalpopups.tpl");
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
        $this->set_value('body',$body);
        $this->set_value('header',"");
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
}

class HomePageContent extends Template
{
    function __construct($topdog, $topdog_count, $server_invite, $bot_invite) {
        parent::__construct('../templates/content_home.tpl');
        $this->set_value('topdog',htmlspecialchars($topdog['name']));
        $this->set_value('topdogid',htmlspecialchars($topdog['id']));
        $this->set_value('topdogcount',$topdog_count);
        $this->set_value('serverinvite', $server_invite);
        $this->set_value('botinvite', $bot_invite);
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

class QuestLog extends Template
{
    function __construct() {
        parent::__construct('../templates/questlog.tpl');
    }  
}

class Leaderboard extends Template {
    private $rankings = array();

    function __construct(){
        parent::__construct('../templates/leaderboard.tpl');
        $this->set_value('logrows',"");
    }

    public function add_row($player){
        $this->rankings[] = new LeaderboardRow($player);
        $this->set_value('logrows', $this->rankings);
    }    
    
}

class LeaderboardRow extends Template {
    function __construct($player){
        parent:: __construct('../templates/leaderboardrow.tpl');
        $this->set_value('playername',$player["name"]);
        $this->set_value('playerid',$player["id"]);
        $this->set_value('totalexp',intval($player["total_exp"]));
        $avatar = get_avatar_url($player);
        if (is_null($avatar))
            $avatar = "https://discordapp.com/assets/dd4dbc0016779df1378e7812eabaa04d.png";      
        $this->set_value('avatar',$avatar);
    }  
}


class StandardLayout extends Layout
{
   function __construct($sidebar,$content = "",$title = '<h2>DueUtil</h2>',$header_buttons = ""){
       parent::__construct('The Worst Discord Bot',$sidebar,$title,$content,$header_buttons);
       $this->set_css("../css/due-style-dash.css");
   }
}

?>
