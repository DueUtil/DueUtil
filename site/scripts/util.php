<?php
require_once("dbconn.php");
require_once("templates.php");


$SUFFIXES = array("st","nd","rd","th");


function int_to_ordinal($number){
    global $SUFFIXES;
    $mod_100 = $number % 100;
    if ($mod_100 > 10 and $mod_100 <= 20)
        $suffix = "th";
    else {
        $index = ($number % 10) - 1;
        if ($index >= 0 && $index < sizeof($SUFFIXES))
            $suffix = $SUFFIXES[$index];
        else
            $suffix = "th";
    }
    return $number.$suffix;
}


function object_to_array($object)
{
    return json_decode(json_encode($object), True);
}


function is_valid_image_url($url) 
{

  if (filter_var($url, FILTER_VALIDATE_URL) && ($headers = get_headers($url))) {
      foreach ($headers as $header) 
          if (strpos($header, 'image/') !== false)
              return True;
  }
  return False;
}


function get_cached_image($image_name){
    foreach (glob($image_name) as $image_found) {
        return $image_found;
    }
    return null;
}


function get_striped_url($url)
{
    $url = preg_replace('/\W+/', '', $url);
    if (strlen($url) > 128)
        return substr($url, 0, 128);
    return $url;
}


function get_cached_image_from_url($url) {
    return get_cached_image('../imagecache/'.get_striped_url($url).'.jpg');
}


function get_avg_stats($dueplayer) 
{
    // 4 - That's how it's done in the bot. Needs to be done that way.
    return array_sum(array($dueplayer["attack"], $dueplayer["strg"], $dueplayer["accy"])) / 4; 
}


function get_object($object_id, $object_collection)
{
    global $manager;
    $find_object_query = new MongoDB\Driver\Query(array('_id' => $object_id));
    $cursor = $manager->executeQuery("dueutil.$object_collection", $find_object_query);
    $data = "data";
    try{
        $object_data = $cursor->toArray();
        if (sizeof($object_data) == 1 && is_object($object_data[0])) {
            $object_data = $object_data[0]->$data;
            $object = json_decode($object_data, True)["py/state"];
            return $object;
        }
        return null;
    } catch (Exception $e) {
        return null;
    }
}


function startsWith($haystack, $needle)
{
     $length = strlen($needle);
     return (substr($haystack, 0, $length) === $needle);
}

function endsWith($haystack, $needle)
{
    $length = strlen($needle);
    if ($length == 0) {
        return true;
    }

    return (substr($haystack, -$length) === $needle);
}


function due_markdown_to_html($markdown)
{
    # Bold
    $markdown = preg_replace('/\*\*(.*?)\*\*/', "<b>$1</b>", $markdown);
    # Underline
    $markdown = preg_replace('/__(.*?)__/', "<u>$1</u>", $markdown);
    # Code
    $markdown = preg_replace('/``(.*?)``/', "<code>$1</code>", $markdown);
    # New lines
    $markdown = str_replace("\n","<br>", $markdown);
    # Prefix
    $markdown = str_replace("[CMD_KEY]",'!', $markdown);
    # Headers
    $markdown = preg_replace('/##(.*?)##/', "<h3>$1</h3>", $markdown);
    # Emoji/Icons
    $markdown = preg_replace('/:icon-(.*?):/', "<span class='icon-$1'></span>", $markdown);
    # Escaped stuff
    $markdown = preg_replace_callback('/\\\(.)/', 
        function ($matches) {
                return htmlspecialchars(substr($matches[0], 1, strlen($matches[0])));;
        }, $markdown);
    # Embeded templates
    preg_match_all('/<TPL:(.*?).tpl>/',$markdown, $matches);
    if (sizeof($matches) > 0) {
        $templates = array();
        foreach($matches[1] as $template_embed) {
            $index = array_search($template_embed, $matches[1]);
            $markdown = str_replace($matches[0][$index], "[@$template_embed]", $markdown);
            $templates[$template_embed] = new StaticContent("$template_embed.tpl");
        }
        $markdown = new StringTemplate($markdown);
        $markdown->set_values($templates);
        $markdown = $markdown->output();
    }
    return $markdown;
}

?>
