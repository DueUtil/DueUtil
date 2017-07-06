<?php

$SUFFIXES = array("st","nd","rd","th");


function int_to_ordinal($number){
    global $SUFFIXES;
    $mod_100 = $number % 100;
    if ($mod_100 > 10 and $mod_100 <= 20)
        $suffix = "th";
    else {
        $index = ($number % 10) - 1;
        if ($index < sizeof($SUFFIXES))
            $suffix = $SUFFIXES[$index];
        else
            $suffix = "th";
    }
    return $number.$suffix;
}


function object_to_array($object)
{
    return json_decode(json_encode($object), true);
}

?>
