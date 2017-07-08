<?php
require_once("dbconn.php");


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

?>
