<?php
require_once("constants.php");
require_once("util.php");


class Embed{
  
    public $title = null;
    public $type = null;
    public $description = null;
    public $url = null;
    public $timestamp = null;
    public $color = null;
    private $fields = null;
    private $footer = null;
    private $image = null;
    private $thumbnail = null;
    private $video = null;
    private $provider = null;
    private $author = null;
    
    
    function __construct($title,$colour,$type="rich") {
        $this->title = $title;
        $this->color = $colour;
        $this->type = $type;
    }
    
    public function add_field($name, $value, $inline=False) {
        if (is_null($this->fields))
            $this->fields = array();
        $this->fields[] = array ('name' => $name,
                                 'value' => $value,
                                 'inline' => $inline);
      
    }
    
    public function set_footer($text, $icon_url="") {
       $this->footer = array('text'=>$text,
                             'icon_url'=>$icon_url);
      
    }
    
    public function set_image($url) {
        $this->image = array('url'=>$url);
    }
    
    public function set_thumbnail ($url) {
        $this->thumbnail = array('url'=>$url);
    }
    
    public function set_video($url) {
        $this->video = array('url'=>$url);
    }
    
    public function set_provider($name, $url) {
        $this->provider = array('name'=>$name,
                                'url'=>$url);
    }
    
    public function set_author($name, $url ="", $icon_url="") {
        $this->author = array('name'=>$name,
                              'url' => $url,
                              'icon_url' => $icon_url);
    }
    
    
    public function toArray() {
        $vars = get_object_vars($this);
        $final_vars = array();
        foreach($vars as $name=>$var) {
            if (!is_null($var))
              $final_vars[$name] = $var;
        }
        return $final_vars;
    }

}


function send_webhook($webhook_url, $params) {
    $webhook = array();
        
    if (isset($params["embeds"])) {
        $webhook["embeds"] = array();
        foreach($params["embeds"] as $embed)
            $webhook["embeds"][] = $embed->toArray();
    }
    
    unset($params["embeds"]);
    
    $webhook = array_merge($webhook, $params);
    
        
    $options = array(
        'http' => array(
            'header'=>  "Content-Type: application/json\r\n" .
                        "Accept: application/json\r\n",
            'method'  => 'POST',
            'content' => json_encode($webhook)
        )
    );
    
    $context  = stream_context_create($options);
    $result = file_get_contents($webhook_url, False, $context);
    if ($result === False) { /* TODO: Handle error */ }

}
?>
